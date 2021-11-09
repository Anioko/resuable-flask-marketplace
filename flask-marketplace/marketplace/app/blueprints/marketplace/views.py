import os
import datetime
import json
import math

import stripe
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort, make_response
from flask_jwt_extended import decode_token, create_access_token
from flask_login import login_required
from flask_rq import get_queue
from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileAllowed
from sqlalchemy import Date
from sqlalchemy.orm import contains_eager, joinedload
from wtforms import Flags

from app import db
from app.blueprints.marketplace.forms import ReviewForm, SearchForm, SVariantForm, SProductForm, SShippingForm, SShippingMethodForm
from app.blueprints.admin.forms import *
from app.blueprints.marketplace.apis import *
from app.blueprints.api import main_api
from app.blueprints.marketplace.paystack import Paystack
from app.decorators import seller_required, buyer_required, anonymous_required
from app.email import send_email
from app.models import MProduct, MProductCategory, MCategory, MBanner, MReview, MVariant, current_user, User, MShippingMethod, MCartDetails, MSettings, MCurrency, \
    MShippingMethodPrice, MOrderItem, MOrder, MSellerOrder, LandingSetting, MBrand, BackgroundImage, SiteLogo

marketplace = Blueprint('marketplace', __name__)
images = UploadSet('images', IMAGES)


# stripe secret key
stripe_secret = os.environ.get(
    'STRIPE_SECRET') 




# Marketplace Shopping Routes start
@marketplace.route('/')
def index():
    form = SearchForm()
    banner = MBanner.query.first()
    background = BackgroundImage.query.first()
    logo = SiteLogo.query.first()
    settings = LandingSetting.query.all()
    website_settings = MSettings.query.first()
    brands = MBrand.query.order_by(MBrand.created_at.asc()).limit(5).all()
    featured_products = MProduct.query.filter_by(availability=True).filter_by(
        is_featured=True).order_by(MProduct.created_at.asc()).limit(4).all()  # .limit(5).all()
    new_arrived_products = MProduct.query.filter_by(
        availability=True).order_by(MProduct.created_at.desc()).limit(4).all()
    categories_instances = MCategory.query.filter_by(is_featured=True).all()
    return render_template('marketplace/landing-page.html', form=form, categories=categories_instances, featured_products=featured_products,
                           new_arrived_products=new_arrived_products, settings=settings, website_settings=website_settings, brands=brands, banner=banner,
                           background=background, logo=logo)


@marketplace.route('/review', methods=['POST'])
def review():
    product_id = int(request.form.get('product_id'))
    product_name = request.form.get('product_name')
    review_text = request.form.get('review_text')
    review_rating = float(request.form.get('review_rating'))
    product_instance = MProduct.query.get_or_404(product_id)
    review = MReview(message=review_text, score=review_rating,
                     user=current_user, product=product_instance)
    db.session.add(review)
    db.session.commit()
    return {
        "status": 1
    }

#'''
# This view is not really necessary.
@marketplace.route('/categories')
def categories():
    categories_list = MCategory.query.filter_by(parent_id=None).all()
    website_settings = MSettings.query.first()
    return render_template('marketplace/categories/index.html', website_settings=website_settings, categories=categories_list)
#'''

@marketplace.route('/category/<int:category_id>/<category_name>', defaults={'page': 1}, methods=['GET'])
@marketplace.route('/category/<int:category_id>/<category_name>/<int:page>', methods=['GET'])
@marketplace.route('/category/<int:category_id>/<category_name>/<int:page>', methods=['GET'])
def category(page, category_id, category_name):
    products = MProduct.query.join(MProductCategory).filter(
        MProductCategory.category_id == category_id).paginate(page, per_page=8)
    website_settings = MSettings.query.first()
    return render_template('marketplace/categories/category.html', website_settings=website_settings, category_id=category_id, category_name=category_name, products=products)


@marketplace.route('/product/<int:product_id>/<product_name>')
def product(product_id, product_name):
    product_instance = db.session.query(MProduct).filter(
        MProduct.id == product_id).options(joinedload(MProduct.variants)).first()
    product_variants = product_instance.variants
    review_form = ReviewForm()
    # print(current_user.name)
    if current_user.is_authenticated:
        current_user_review = MReview.query.filter_by(
            user=current_user).filter_by(product=product_instance).first()
    website_settings = MSettings.query.first()
    # if current_user.is_authenticated and current_user.is_seller:
    #     can_review = False
    # elif current_user.is_authenticated and current_user_review:
    #     can_review = False
    # elif current_user.is_authenticated and not current_user_review:
    #     can_review = True
    # else:
    #     can_review = False
    can_review = True if current_user.is_authenticated and not current_user_review else False

    settings = LandingSetting.query.all()
    return render_template('marketplace/products/product.html', website_settings=website_settings, review_form=review_form,
                           can_review=can_review, product_instance=product_instance, settings=settings)


@marketplace.route('/seller/<int:seller_id>/products')
def view_seller_products(seller_id):
    seller = User.query.filter_by(id=seller_id).filter_by(
        is_seller=True).first_or_404()
    avail_products = MProduct.query.filter_by(
        seller=seller).filter_by(availability=True).all()
    not_avail_products = MProduct.query.filter_by(
        seller=seller).filter_by(availability=False).all()
    website_settings = MSettings.query.first()
    return render_template('marketplace/products/seller.html', website_settings=website_settings, avail_products=avail_products,
                           not_avail_products=not_avail_products)


@marketplace.route('/cart')
def cart():
    cart_instance = get_current_cart()
    website_settings = MSettings.query.first()
    if cart_instance.products_count == 0:
        cart_instance.step = 1
        return render_template('marketplace/cart/no_items.html', website_settings=website_settings)
    if cart_instance.step != 1:
        return redirect(url_for('marketplace.order', step=cart_instance.step))
    return render_template('marketplace/cart/index.html', website_settings=website_settings, cart=cart_instance)


@marketplace.route('/order/<int:step>', methods=['GET', 'POST'])
def order(step):
    cart_instance = get_current_cart()
    website_settings = MSettings.query.first()
    if cart_instance.products_count == 0:
        cart_instance.step = 1
        return render_template('marketplace/cart/no_items.html', website_settings=website_settings)

    if request.method == 'POST':
        if step == 1:
            cart_instance.step = 1
            return redirect(url_for('marketplace.cart'))

        elif step == 2:
            print("Enter your details")
            if cart_instance.step == 1:
                for item in cart_instance.cart_items:
                    product_instance = item.product
                    if item.count < product_instance.min_order_quantity:
                        flash("You cannot buy less than {} pieces of the product {}".format(
                            product_instance.min_order_quantity, product_instance.name), 'error')
                        return redirect(url_for('marketplace.cart'))
                cart_instance.step = 2
                return redirect(url_for('marketplace.order', step=2))

            if cart_instance.step == 3:
                cart_instance.step = 2
                MCartDetails.query.filter_by(cart=cart_instance).delete()
                items = MCartItem.query.filter_by(cart=cart_instance).all()
                for item in items:
                    item.shipping_method = None
                    db.session.add(item)
                db.session.commit()
                return redirect(url_for('marketplace.order', step=2))

            if cart_instance.step == 2:
                return redirect(url_for('marketplace.order', step=2))

        elif step == 3:
            print("Now enter your stripe")
            form = SShippingForm()
            valid = True
            for seller_cart in cart_instance.seller_carts:
                input_field = "shipping[{}]".format(seller_cart.seller.id)
                val = request.form.get(input_field)
                if not val:
                    valid = False
                    form.errors[input_field] = ['This Field is Required']
                elif not MShippingMethod.query.get(val):
                    form.errors[input_field] = [
                        'Not A Valid Choice, Pls Try Again']
                    valid = False
            if not current_user.is_authenticated:
                user = User.query.filter_by(email=form.email.data).first()
                if user:
                    flash(
                        'There is a mediville user with this email, choose another email or login instead', 'error')
                    valid = False
            if not valid:
                form.process(request.form)
                return render_template('marketplace/cart/order_shipping.html', cart=cart_instance, form=form, website_settings=website_settings)

            if form.validate_on_submit():
                cart_details = MCartDetails(
                    cart=cart_instance,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    mobile_phone=form.mobile_phone.data,
                    state=form.state.data,
                    zip=form.zip.data,
                    country=form.country.data,
                    city=form.city.data,
                )
                db.session.add(cart_details)
                for seller_cart in cart_instance.seller_carts:
                    input_field = "shipping[{}]".format(seller_cart.seller.id)
                    val = request.form.get(input_field)
                    shipping = MShippingMethod.query.get(val)
                    seller_cart.shipping_method = shipping
                    db.session.add(seller_cart)
                db.session.commit()
                cart_instance.step = 3

                stripe_public = MSettings.query.filter_by(
                    name='stripe_public').first()
                paystack_public = MSettings.query.filter_by(
                    name='paystack_public').first()
                if not stripe_public or not paystack_public:
                    MSettings.insert_stripe()

                stripe_public = stripe_public.value
                paystack_public = paystack_public.value

                if paystack_public != "None" and stripe_public == 'None':
                    products_total = cart_instance.products_total
                    order_currency = cart_instance.currency
                    email = cart_instance.cart_details.email
                    order_number = cart_instance.generate_order_number()
                    shipping_cost = cart_instance.price_shipping()
                    order_total = products_total + shipping_cost
                    order_discount = 0
                    order_pay_amount = order_total - order_discount
                    price_to_pay = cart_instance.price_paid()
                    description = "Payment for buying from {{ config.APP_NAME }} Markeplace for order: " + order_number
                    if not order_pay_amount == price_to_pay:
                        flash("Calculation Mismatch, Please Try Again", "error")
                        return redirect(url_for('marketplace.order', step=3))
                    paystack_currency = MCurrency.query.all()
                    paystack_currency = paystack_currency[0].name if paystack_currency else 'NGN'
                    print(paystack_currency)
                    paystack_instance = Paystack(token=paystack_public)
                    user_id = current_user.id if current_user.is_authenticated else None
                    response = paystack_instance.accept(
                        amount=math.ceil(order_pay_amount * 100),
                        currency=paystack_currency,
                        email=email,
                        description=description,
                        metadata={"card_id": cart_instance.id,
                                  'user_id': user_id, }
                    )

                    print(response)

                    if not response.get('status'):
                        error_msg = response.get('message')
                        flash(error_msg, 'danger')
                        return redirect(url_for('marketplace.order', step=3))
                    authorization_url = response.get(
                        'data').get('authorization_url')
                    print(authorization_url)
                    return redirect(authorization_url)
                return redirect(url_for('marketplace.order', step=3))
            else:
                return render_template('marketplace/cart/order_shipping.html', cart=cart_instance, form=form, website_settings=website_settings)

        elif step == 4:
            print("You\'re now a legend")
            buyer = None
            if current_user.is_authenticated:
                buyer = current_user

            # order calculations
            products_total = cart_instance.products_total
            order_currency = cart_instance.currency
            email = cart_instance.cart_details.email
            order_number = cart_instance.generate_order_number()
            shipping_cost = cart_instance.price_shipping()
            order_total = products_total + shipping_cost
            order_discount = 0
            order_pay_amount = order_total - order_discount
            price_to_pay = cart_instance.price_paid()
            description = "Payment for buying from {{ config.APP_NAME }} Markeplace for order: " + order_number
            if not order_pay_amount == price_to_pay:
                flash("Calculation Mismatch, Please Try Again", "error")
                return redirect(url_for('marketplace.order', step=3))
            stripe.api_key = stripe_secret
            customer = stripe.Customer.create(
                email=email,
                card=request.form['stripeToken']
            )
            token = request.form['stripeToken']
            try:
                charge = stripe.Charge.create(
                    amount=math.ceil(order_pay_amount * 100),
                    currency=order_currency.name.lower(),
                    description=description,
                    customer=customer,
                )
                if charge:
                    flash('Thanks for paying!', 'success')
                    order_instance = MOrder(
                        order_number=order_number,
                        charge_id=charge.id,
                        products_total=products_total,
                        shipping_cost=shipping_cost,
                        order_total=order_total,
                        order_discount=order_discount,
                        order_pay_amount=order_pay_amount,
                        buyer=buyer,
                        price_currency=order_currency,
                        first_name=cart_instance.cart_details.first_name,
                        last_name=cart_instance.cart_details.last_name,
                        email=cart_instance.cart_details.email,
                        mobile_phone=cart_instance.cart_details.mobile_phone,
                        zip=cart_instance.cart_details.zip,
                        city=cart_instance.cart_details.city,
                        state=cart_instance.cart_details.state,
                        country=cart_instance.cart_details.country,
                    )
                    db.session.add(order_instance)
                    db.session.commit()
                    db.session.refresh(order_instance)
                    for seller_cart in cart_instance.seller_carts:
                        seller_order = MSellerOrder(
                            order=order_instance,
                            seller=seller_cart.seller,
                            shipping_method=seller_cart.shipping_method,
                            buyer=seller_cart.buyer,
                            currency=seller_cart.currency,
                        )
                        db.session.add(seller_order)
                        db.session.commit()
                        db.session.refresh(seller_order)
                    for cart_item in seller_cart.cart_items:

                        order_item = MOrderItem(
                            order=order_instance,
                            seller_order=seller_order,
                            seller=cart_item.seller,
                            buyer=buyer,
                            product=cart_item.product,
                            count=cart_item.count,
                            current_price=cart_item.product.price,
                            current_total_price=cart_item.product.price*cart_item.count,
                        )
                        db.session.add(order_item)
                        db.session.commit()

                    MCartItem.query.filter_by(cart=cart_instance).delete()
                    MSellerCart.query.filter_by(cart=cart_instance).delete()
                    MCartDetails.query.filter_by(cart=cart_instance).delete()
                    MCart.query.filter_by(id=cart_instance.id).delete()
                    db.session.commit()
                    return render_template('marketplace/cart/order_done.html', order=order_instance, website_settings=website_settings)
            except stripe.error.CardError as e:
                flash('Oops. Something is wrong with your card info!', 'danger')
                return redirect(url_for('marketplace.order', step=3))
        return abort(404)

    elif request.method == 'GET':
        if cart_instance.step != step:
            return redirect(url_for('marketplace.order', step=cart_instance.step))
        if step == 2:
            form = SShippingForm()
            if current_user.is_authenticated:
                form.first_name.data = current_user.first_name
                form.last_name.data = current_user.last_name
                form.email.data = current_user.email
                form.mobile_phone.data = current_user.mobile_phone
                form.state.data = current_user.state
                form.zip.data = current_user.zip
                form.country.data = current_user.country
                form.city.data = current_user.city
            return render_template('marketplace/cart/order_shipping.html', cart=cart_instance, form=form, website_settings=website_settings)

        elif step == 3:
            stripe_public = MSettings.query.filter_by(
                name='stripe_public').first()
            stripe_public = stripe_public.value
            print(stripe_public)
            if not cart_instance.cart_details:
                cart_instance.step = 2
                return redirect(url_for('marketplace.order', step=2))
            return render_template('marketplace/cart/order_payment.html', cart=cart_instance, website_settings=website_settings,
                                   stripe_public=stripe_public)
        return abort(404)

# create a new flask route to act as a callback for Paystack
# localhost:5000/marketplace/paystack/callback


@ marketplace.route('/paystack/callback', methods=['GET', 'POST'])
def paystack_callback():
    if request.method == 'POST':
        payment_data = request.get_json(force=True)
        print(payment_data)
        if not payment_data.get('event') == 'charge.success':
            return '', 200

        if not payment_data.get('data').get('status') == 'success':
            return '', 200

        reference = payment_data.get('data').get('reference')
        channel = payment_data.get('data').get('channel')
        currency = payment_data.get('data').get('currency')
        amount = payment_data.get('data').get('amount')
        payment_id = payment_data.get('data').get('id')
        cart_id = payment_data.get('data').get('metadata').get('card_id')
        user_id = payment_data.get('data').get('metadata').get('user_id')
        cart_instance = get_current_cart({
            'user_id': user_id,
            'cart_id': cart_id,
        })
        buyer = User.query.filter_by(id=user_id).first()

        # order calculations
        products_total = cart_instance.products_total
        order_currency = cart_instance.currency
        email = cart_instance.cart_details.email
        order_number = cart_instance.generate_order_number()
        shipping_cost = cart_instance.price_shipping()
        order_total = products_total + shipping_cost
        order_discount = 0
        order_pay_amount = order_total - order_discount
        price_to_pay = cart_instance.price_paid()
        description = "Payment for buying from {{ config.APP_NAME }} Markeplace for order: " + order_number
        if not order_pay_amount == price_to_pay:
            flash("Calculation Mismatch, Please Try Again", "error")
            print("Calculation Mismatch, Please Try Again", "error")
            return '', 200

        flash('Thanks for paying!', 'success')
        print('Thanks for paying!', 'success')
        order_instance = MOrder(
            order_number=order_number,
            charge_id=payment_id,
            products_total=products_total,
            shipping_cost=shipping_cost,
            order_total=order_total,
            order_discount=order_discount,
            order_pay_amount=order_pay_amount,
            buyer=buyer,
            price_currency=order_currency,
            first_name=cart_instance.cart_details.first_name,
            last_name=cart_instance.cart_details.last_name,
            email=cart_instance.cart_details.email,
            mobile_phone=cart_instance.cart_details.mobile_phone,
            zip=cart_instance.cart_details.zip,
            city=cart_instance.cart_details.city,
            state=cart_instance.cart_details.state,
            country=cart_instance.cart_details.country,
        )
        db.session.add(order_instance)
        db.session.commit()
        db.session.refresh(order_instance)
        for seller_cart in cart_instance.seller_carts:
            seller_order = MSellerOrder(
                order=order_instance,
                seller=seller_cart.seller,
                shipping_method=seller_cart.shipping_method,
                buyer=seller_cart.buyer,
                currency=seller_cart.currency,
            )
            db.session.add(seller_order)
            db.session.commit()
            db.session.refresh(seller_order)
        for cart_item in seller_cart.cart_items:

            order_item = MOrderItem(
                order=order_instance,
                seller_order=seller_order,
                seller=cart_item.seller,
                buyer=buyer,
                product=cart_item.product,
                count=cart_item.count,
                current_price=cart_item.product.price,
                current_total_price=cart_item.product.price*cart_item.count,
            )
            db.session.add(order_item)
            db.session.commit()

        MCartItem.query.filter_by(cart=cart_instance).delete()
        MSellerCart.query.filter_by(cart=cart_instance).delete()
        MCartDetails.query.filter_by(cart=cart_instance).delete()
        MCart.query.filter_by(id=cart_instance.id).delete()
        db.session.commit()
        return '', 200
    else:
        return '', 200

# Marketplace Shopping end


# Marketplace Seller Panel start
@ marketplace.route('/seller-panel')
@ login_required
@ seller_required
def seller_panel():
    website_settings = MSettings.query.first()
    return render_template("marketplace/seller/index.html", website_settings=website_settings)


@ marketplace.route('/seller-panel/stats')
@ login_required
@ seller_required
def seller_stats():
    website_settings = MSettings.query.first()
    orders_count = MSellerOrder.query.filter_by(seller=current_user).count()
    today_orders_count = MSellerOrder.query.filter_by(seller=current_user).filter(
        MSellerOrder.created_at.cast(Date) == datetime.datetime.now().date()).count()
    currencies = MCurrency.query.all()
    revenue = []
    for currency in currencies:
        orders = MSellerOrder.query.filter_by(
            seller=current_user).filter_by(currency=currency).all()
        print(len(orders), current_user.id)
        currency_sum = 0
        for order_instance in orders:
            currency_sum += order_instance.total_price
        revenue.append({'currency': currency, 'revenue': currency_sum})

    return render_template("marketplace/seller/stats.html", orders_count=orders_count, revenue=revenue, today_orders_count=today_orders_count, website_settings=website_settings)


@ marketplace.route('/seller-panel/orders', defaults={'page': 1}, methods=['GET'])
@ marketplace.route('/seller-panel/orders/<int:page>', methods=['GET'])
@ login_required
@ seller_required
def seller_orders(page):
    website_settings = MSettings.query.first()
    orders = MSellerOrder.query.filter_by(
        seller=current_user).paginate(page, per_page=50)
    orders_count = MSellerOrder.query.filter_by(seller=current_user).count()
    return render_template('marketplace/seller/orders/index.html', website_settings=website_settings, orders=orders, orders_count=orders_count)


@ marketplace.route('/seller-panel/order/<int:order_id>/view', methods=['GET'])
@ login_required
@ seller_required
def seller_order_view(order_id):
    website_settings = MSettings.query.first()
    order_instance = MSellerOrder.query.get_or_404(order_id)
    return render_template('marketplace/seller/orders/order.html', website_settings=website_settings, order=order_instance)


@ marketplace.route('/seller-panel/coupons', defaults={'page': 1}, methods=['GET'])
@ marketplace.route('/seller-panel/coupons/<int:page>', methods=['GET'])
@ login_required
@ seller_required
def seller_coupons(page):
    website_settings = MSettings.query.first()
    return render_template('marketplace/seller/coupons/index.html', website_settings=website_settings)


@ marketplace.route('/seller-panel/products', defaults={'page': 1}, methods=['GET'])
@ marketplace.route('/seller-panel/products/<int:page>', methods=['GET'])
@ login_required
@ seller_required
def seller_products(page):
    website_settings = MSettings.query.first()
    products = MProduct.query.filter_by(seller_id=current_user.id).order_by(MProduct.created_at.asc()).paginate(page,
                                                                                                                per_page=4)
    products_count = MProduct.query.filter_by(
        seller_id=current_user.id).count()
    return render_template('marketplace/seller/products.html', products=products, products_count=products_count, website_settings=website_settings)


@ marketplace.route('/seller-panel/products/add', methods=['GET', 'POST'])
@ login_required
@ seller_required
def seller_product_create():
    website_settings = MSettings.query.first()
    form = SProductForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image_filenames = []
            if request.files['images']:
                image_files = request.files.getlist('images')
                for image in image_files:
                    image_filename = images.save(image)
                    image_filenames.append(image_filename)
            image_filenames = json.dumps(image_filenames)
            prod = MProduct(
                name=form.name.data,
                images=image_filenames,
                seller=current_user,
                description=form.description.data,
                is_featured=form.is_featured.data,
                categories=form.categories.data,
                # variants=form.variants.data,
                condition=form.condition.data,
                brand=form.brand.data,
                availability=form.availability.data,
                min_order_quantity=form.min_order_quantity.data,
                length=form.length.data,
                weight=form.weight.data,
                height=form.height.data,
                price=form.price.data,
                price_currency=form.price_currency.data,
                lead_time=form.lead_time.data
            )
            db.session.add(prod)
            db.session.commit()
            flash('Product {} successfully created'.format(prod.name), 'success')
            return redirect(url_for('marketplace.seller_products'))
    return render_template('marketplace/seller/products-add-edit.html', website_settings=website_settings, form=form)


@ marketplace.route('/seller-panel/products/<int:product_id>/edit', methods=['GET', 'POST'])
@ login_required
@ seller_required
def seller_product_edit(product_id):
    website_settings = MSettings.query.first()
    product_instance = MProduct.query.filter_by(
        seller=current_user).filter_by(id=product_id).first_or_404()
    form = SProductForm(obj=product_instance)
    form.images.validators = [FileAllowed(images, 'Images only!')]
    form.images.flags = Flags()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                image_filenames = request.form.getlist('old_images[]')
            except:
                image_filenames = []
            if request.files['images']:
                image_files = request.files.getlist('images')
                for image in image_files:
                    image_filename = images.save(image)
                    image_filenames.append(image_filename)
            image_filenames = json.dumps(image_filenames)
            product_instance.name = form.name.data
            product_instance.is_featured = form.is_featured.data
            product_instance.seller = current_user
            product_instance.images = image_filenames
            product_instance.description = form.description.data
            product_instance.categories = form.categories.data
            product_instance.variants = form.variants.data
            product_instance.condition = form.condition.data
            product_instance.brand = form.brand.data
            product_instance.availability = form.availability.data
            product_instance.min_order_quantity = form.min_order_quantity.data
            product_instance.length = form.length.data
            product_instance.weight = form.weight.data
            product_instance.height = form.height.data
            product_instance.price = form.price.data
            product_instance.price_currency = form.price_currency.data
            product_instance.lead_time = form.lead_time.data
            db.session.add(product_instance)
            db.session.commit()
            flash('Product {} successfully Updated'.format(
                product_instance.name), 'success')
            return redirect(url_for('marketplace.seller_products'))
    return render_template('marketplace/seller/products-add-edit.html', website_settings=website_settings, form=form, product=product_instance)


@ marketplace.route('/seller-panel/products/<int:product_id>/delete', methods=['POST'])
@ login_required
@ seller_required
def seller_product_delete(product_id):
    website_settings = MSettings.query.first()
    cat = MProduct.query.filter_by(
        seller=current_user).filter_by(id=product_id).first()
    if not cat:
        abort(404)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Product.', 'success')
    return redirect(url_for('marketplace.seller_products'))


@ marketplace.route('/seller-panel/shipping_methods', defaults={'page': 1}, methods=['GET'])
@ marketplace.route('/seller-panel/shipping_methods/<int:page>', methods=['GET'])
@ login_required
@ seller_required
def marketplace_shipping_methods(page):
    website_settings = MSettings.query.first()
    shipping_methods = MShippingMethod.query.filter_by(seller=current_user).order_by(
        MShippingMethod.created_at.asc()).paginate(page, per_page=50)
    shipping_methods_count = MShippingMethod.query.filter_by(
        seller=current_user).count()
    return render_template('marketplace/seller/shipping_methods/index.html', website_settings=website_settings, shipping_methods=shipping_methods,
                           shipping_methods_count=shipping_methods_count)


@ marketplace.route('/seller-panel/shipping_methods/add', methods=['GET', 'POST'])
@ login_required
@ seller_required
def marketplace_shipping_method_create():
    website_settings = MSettings.query.first()
    form = SShippingMethodForm()
    currencies = MCurrency.query.all()
    if request.method == 'POST':
        if form.validate_on_submit():
            valid = True
            for currency in currencies:
                input_field = 'price[{}]'.format(currency.id)
                if not request.form.get(input_field):
                    valid = False
                    form.errors[input_field] = ['This Field is Required']
            if not valid:
                form.process(request.form)
                return render_template('marketplace/seller/shipping_methods/add-edit.html', form=form,
                                       currencies=currencies)
            shipping_method = MShippingMethod(
                name=form.name.data,
                seller=current_user
            )
            db.session.add(shipping_method)
            db.session.commit()
            db.session.refresh(shipping_method)
            for currency in currencies:
                input_field = 'price[{}]'.format(currency.id)
                shipping_method_price = MShippingMethodPrice(
                    shipping_method=shipping_method,
                    seller=current_user,
                    price_currency=currency,
                    price=request.form.get(input_field)
                )
                db.session.add(shipping_method_price)
                db.session.commit()
            flash('Shipping Method {} successfully created'.format(
                shipping_method.name), 'success')
            return redirect(url_for('marketplace.marketplace_shipping_methods'))
    return render_template('marketplace/seller/shipping_methods/add-edit.html', website_settings=website_settings, form=form, currencies=currencies)


@ marketplace.route('/seller-panel/shipping_methods/<int:shipping_method_id>/edit', methods=['GET', 'POST'])
@ login_required
@ seller_required
def marketplace_shipping_method_edit(shipping_method_id):
    website_settings = MSettings.query.first()
    shipping_method = MShippingMethod.query.filter_by(id=shipping_method_id).filter_by(
        seller=current_user).first_or_404()
    form = SShippingMethodForm(obj=shipping_method)
    currencies = MCurrency.query.all()
    if request.method == 'POST':
        if form.validate_on_submit():
            valid = True
            for currency in currencies:
                input_field = 'price[{}]'.format(currency.id)
                if not request.form.get(input_field):
                    valid = False
                    form.errors[input_field] = ['This Field is Required']
            if not valid:
                form.process(request.form)
                return render_template('marketplace/seller/shipping_methods/add-edit.html', form=form, website_settings=website_settings,
                                       currencies=currencies)

            shipping_method.name = form.name.data
            shipping_method.seller = current_user
            db.session.add(shipping_method)
            db.session.commit()
            db.session.refresh(shipping_method)
            for currency in currencies:
                input_field = 'price[{}]'.format(currency.id)
                shipping_method_price = MShippingMethodPrice.query.filter_by(
                    shipping_method=shipping_method).filter_by(price_currency=currency).first()
                if not shipping_method_price:
                    shipping_method_price = MShippingMethodPrice(
                        shipping_method=shipping_method,
                        price_currency=currency,
                    )
                shipping_method_price.price = request.form.get(input_field)
                db.session.add(shipping_method_price)
                db.session.commit()
            flash('Shipping Method {} successfully Updated'.format(
                shipping_method.name), 'success')
            return redirect(url_for('marketplace.marketplace_shipping_methods'))
    return render_template('marketplace/seller/shipping_methods/add-edit.html', form=form, currencies=currencies, website_settings=website_settings)


@ marketplace.route('/seller-panel/shipping_methods/<int:shipping_method_id>/_delete', methods=['POST'])
@ login_required
@ seller_required
def marketplace_shipping_method_delete(shipping_method_id):
    website_settings = MSettings.query.first()
    cat = MShippingMethod.query.get_or_404(shipping_method_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Shipping Method.', 'success')
    return redirect(url_for('marketplace.marketplace_shipping_methods'))


@ marketplace.route('/buyer-panel')
@ buyer_required
def buyer_panel():
    website_settings = MSettings.query.first()
    return render_template("marketplace/buyer/index.html", website_settings=website_settings)


@ marketplace.route('/anon-login', methods=['GET', 'POST'])
@ anonymous_required
def anon_login():
    website_settings = MSettings.query.first()
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash("Please provide a valid email", "error")
            return render_template("marketplace/buyer/anon_auth.html", website_settings=website_settings)
        user = User.query.filter_by(email=email).first()
        if user:
            flash(
                "There is a user with this email, please go to the login page instead", "error")
            return render_template("marketplace/buyer/anon_auth.html", website_settings=website_settings)
        orders_count = MOrder.query.filter_by(email=email).count()
        if orders_count == 0:
            flash("There is a no orders associated with this email on our database, please insert an email you made "
                  "orders with", "error")
            return render_template("marketplace/buyer/anon_auth.html", website_settings=website_settings)
        token = create_access_token(identity=request.form.get(
            'email'), expires_delta=datetime.timedelta(hours=24))
        get_queue().enqueue(
            send_email,
            recipient=email,
            subject='You Have a new notification on Mediville',
            template='account/email/anon_auth',
            link=url_for('marketplace.anon_auth', token=token, _external=True),
            user=None
        )
        flash("Auth link were sent to {}".format(email), "success")
    return render_template("marketplace/buyer/anon_auth.html", website_settings=website_settings)

##########################################################################################


@ marketplace.route('/seller-panel/variants', defaults={'page': 1}, methods=['GET'])
@ marketplace.route('/seller-panel/variants/<int:page>', methods=['GET'])
@ login_required
@ seller_required
def seller_variants(page):
    website_settings = MSettings.query.first()
    variants = MVariant.query.order_by(MVariant.created_at.asc()).paginate(page,
                                                                           per_page=50)
    variants_count = MVariant.query.count()
    return render_template('marketplace/seller/variants.html', website_settings=website_settings, variants=variants, variants_count=variants_count)


@ marketplace.route('/seller-panel/variants/add', methods=['GET', 'POST'])
@ login_required
@ seller_required
def seller_variant_create():
    website_settings = MSettings.query.first()
    form = SVariantForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            var = MVariant(
                name=form.name.data,
                symbol=form.symbol.data
            )
            db.session.add(var)
            db.session.commit()
            flash('Variant {} successfully created'.format(var.name), 'success')
            return redirect(url_for('marketplace.seller_variants'))
    return render_template('marketplace/seller/variants-add-edit.html', website_settings=website_settings, form=form)


@ marketplace.route('/seller-panel/variants/<int:variant_id>/edit', methods=['GET', 'POST'])
@ login_required
@ seller_required
def seller_variant_edit(variant_id):
    website_settings = MSettings.query.first()
    variant_instance = MVariant.query.filter_by(id=variant_id).first_or_404()
    form = SVariantForm(obj=variant_instance)
    if request.method == 'POST':
        if form.validate_on_submit():
            variant_instance.name = form.name.data
            variant_instance.symbol = form.symbol.data
            db.session.add(variant_instance)
            db.session.commit()
            flash('Variant {} successfully Updated'.format(
                variant_instance.name), 'success')
            return redirect(url_for('marketplace.seller_variants'))
    return render_template('marketplace/seller/variants-add-edit.html', website_settings=website_settings, form=form, product=variant_instance)


@ marketplace.route('/seller-panel/variants/<int:variant_id>/_delete', methods=['POST'])
@ login_required
@ seller_required
def seller_variant_delete(variant_id):
    website_settings = MSettings.query.first()
    var = MVariant.query.get_or_404(variant_id)
    db.session.delete(var)
    db.session.commit()
    flash('Successfully deleted Variant.', 'success')
    return redirect(url_for('marketplace.seller_variants'))

##########################################################################################


@ marketplace.route('/anon-auth/<token>')
@ anonymous_required
def anon_auth(token):
    website_settings = MSettings.query.first()
    try:
        token_decoded = decode_token(token)
    except:
        flash("Invalid or expired link", 'error')
        return redirect(url_for('marketplace.anon_login'))

    email = token_decoded['identity']
    new_token = create_access_token(
        identity=email, expires_delta=datetime.timedelta(days=30))
    resp = make_response(redirect(url_for('marketplace.buyer_panel')))
    resp.set_cookie('buyer_jwt', new_token)
    return resp


@ marketplace.route('/buyer-panel/orders', defaults={'page': 1}, methods=['GET'])
@ marketplace.route('/buyer-panel/orders/<int:page>', methods=['GET'])
@ buyer_required
def buyer_orders(page):
    website_settings = MSettings.query.first()
    if current_user.is_authenticated:
        orders = MOrder.query.filter_by(
            buyer=current_user).paginate(page, per_page=50)
        orders_count = MOrder.query.filter_by(buyer=current_user).count()
    else:
        buyer_jwt = request.cookies.get('buyer_jwt')
        if not buyer_jwt:
            return redirect(url_for('marketplace.anon_login'))
        try:
            token_decoded = decode_token(buyer_jwt)
            email = token_decoded['identity']
            orders = MOrder.query.filter_by(
                email=email).paginate(page, per_page=50)
            orders_count = MOrder.query.filter_by(email=email).count()
        except:
            flash("Session expired authenticate again, please", 'error')
            return redirect(url_for('marketplace.anon_login'))
    return render_template('marketplace/buyer/orders/index.html', website_settings=website_settings, orders=orders, orders_count=orders_count)


@ marketplace.route('/buyer-panel/order/<int:order_id>/view', methods=['GET'])
@ buyer_required
def buyer_order_view(order_id):
    website_settings = MSettings.query.first()
    order_instance = MOrder.query.get_or_404(order_id)
    return render_template('marketplace/buyer/orders/order.html', website_settings=website_settings, order=order_instance)


@ marketplace.route('/marketplace/brands/add', methods=['GET', 'POST'])
@ login_required
@ seller_required
def marketplace_brand_create():
    website_settings = MSettings.query.first()
    form = MBrandForm()
    form.image.validators = [FileAllowed(images, 'Images only!')]
    form.image.flags = Flags()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                image_filenames = request.form.getlist('old_images[]')
            except:
                image_filenames = []
            if request.files['image']:
                image_files = request.files.getlist('image')
                for image in image_files:
                    image_filename = images.save(image)
                    image_filenames.append(image_filename)
            image_filenames = json.dumps(image_filenames)
            brand = MBrand(
                name=form.name.data,
                image=image_filenames)
            db.session.add(brand)
            db.session.commit()
            flash('Brand {} successfully created'.format(brand.name), 'success')
            return redirect(url_for('marketplace.seller_product_create'))
    return render_template('marketplace/seller/brands/add-edit.html', website_settings=website_settings, form=form)


# APIS
main_api.add_resource(AddToCart, '/add_to_cart')
main_api.add_resource(SubFromCart, '/sub_from_cart')
main_api.add_resource(RemoveFromCart, '/remove_from_cart')
main_api.add_resource(ChangeCartItemQuantity, '/change_cart_item_quantity')
main_api.add_resource(CartCount, '/cart_count')
main_api.add_resource(OrderSummary, '/order_summary/<int:step>/<int:delivery>')
main_api.add_resource(ChangeOrderStatus, '/seller-panel/change_order_status')
