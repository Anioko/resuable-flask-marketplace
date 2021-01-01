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
from wtforms import Flags

from app import db
from app.blueprints.marketplace.forms import SProductForm, SShippingForm, SShippingMethodForm
from app.blueprints.marketplace.apis import *
from app.blueprints.api import main_api
from app.decorators import seller_required, buyer_required, anonymous_required
from app.email import send_email
from app.models import MProduct, MCategory, current_user, User, MShippingMethod, MCartDetails, MSettings, MCurrency, \
    MShippingMethodPrice, MOrderItem, MOrder, MSellerOrder, LandingSetting, OurBrand, NewsLink

marketplace = Blueprint('marketplace', __name__)
images = UploadSet('images', IMAGES)


# Marketplace Shopping Routes start
@marketplace.route('/')
def index():

    settings = LandingSetting.query.all()
    brands = OurBrand.query.all()
    newslinks = NewsLink.query.all()
    products = MProduct.query.filter_by(availability=True).filter_by(is_featured=True).all()#.limit(5).all()
    categories_instances = MCategory.query.filter_by(is_featured=True).all()
    return render_template('marketplace/page-index-3.html', categories=categories_instances, products=products,
                           settings=settings, brands=brands, newslinks=newslinks)


@marketplace.route('/categories')
def categories():
    categories_list = MCategory.query.filter_by(parent_id=None).all()
    return render_template('marketplace/categories/index.html', categories=categories_list)


@marketplace.route('/category/<int:category_id>/<category_name>')
def category(category_id, category_name):
    category_instance = MCategory.query.get_or_404(category_id, category_name)
    return render_template('marketplace/categories/category.html', category_instance=category_instance)


@marketplace.route('/product/<int:product_id>/<product_name>')
def product(product_id, product_name):
    settings = LandingSetting.query.all()
    product_instance = MProduct.query.get_or_404(product_id, product_name)
    return render_template('marketplace/products/product.html', product_instance=product_instance, settings=settings)


@marketplace.route('/seller/<int:seller_id>/products')
def view_seller_products(seller_id):
    seller = User.query.filter_by(id=seller_id).filter_by(is_seller=True).first_or_404()
    avail_products = MProduct.query.filter_by(seller=seller).filter_by(availability=True).all()
    not_avail_products = MProduct.query.filter_by(seller=seller).filter_by(availability=False).all()
    return render_template('marketplace/products/seller.html', avail_products=avail_products,
                           not_avail_products=not_avail_products)


@marketplace.route('/cart')
def cart():
    cart_instance = get_current_cart()
    if cart_instance.products_count == 0:
        cart_instance.step = 1
        return render_template('marketplace/cart/no_items.html')
    if cart_instance.step != 1:
        return redirect(url_for('marketplace.order', step=cart_instance.step))
    return render_template('marketplace/cart/index.html', cart=cart_instance)


@marketplace.route('/order/<int:step>', methods=['GET', 'POST'])
def order(step):
    cart_instance = get_current_cart()
    if cart_instance.products_count == 0:
        cart_instance.step = 1
        return render_template('marketplace/cart/no_items.html')

    if request.method == 'POST':
        if step == 1:
            cart_instance.step = 1
            return redirect(url_for('marketplace.cart'))

        elif step == 2:
            if cart_instance.step == 1:
                for item in cart_instance.cart_items:
                    product_instance = item.product
                    if item.count < product_instance.min_order_quantity:
                        flash("You cannot buy less than {} pieces of the product {}".format(product_instance.min_order_quantity, product_instance.name), 'error')
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
            form = SShippingForm()
            valid = True
            for seller_cart in cart_instance.seller_carts:
                input_field = "shipping[{}]".format(seller_cart.seller.id)
                val = request.form.get(input_field)
                if not val:
                    valid = False
                    form.errors[input_field] = ['This Field is Required']
                elif not MShippingMethod.query.get(val):
                    form.errors[input_field] = ['Not A Valid Choice, Pls Try Again']
                    valid = False
            if not current_user.is_authenticated:
                user = User.query.filter_by(email=form.email.data).first()
                if user:
                    flash('There is a mediville user with this email, choose another email or login instead', 'error')
                    valid = False
            if not valid:
                form.process(request.form)
                return render_template('marketplace/cart/order_shipping.html', cart=cart_instance, form=form)

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
                return redirect(url_for('marketplace.order', step=3))
            else:
                return render_template('marketplace/cart/order_shipping.html', cart=cart_instance, form=form)
        elif step == 4:
            buyer = None
            if current_user.is_authenticated:
                buyer = current_user
            # order calculations
            products_total = cart_instance.products_total
            order_currency = cart_instance.currency

            order_number = cart_instance.generate_order_number()
            shipping_cost = cart_instance.price_shipping()
            order_total = products_total + shipping_cost
            order_discount = 0
            order_pay_amount = order_total - order_discount
            price_to_pay = cart_instance.price_paid()
            description = "Payment for buying from Mediville Markeplace for order: " + order_number
            if not order_pay_amount == price_to_pay:
                flash("Calculation Mismatch, Please Try Again", "error")
                return redirect(url_for('marketplace.order', step=3))
            stripe_secret = MSettings.query.filter_by(name='stripe_secret').first()
            if not stripe_secret:
                MSettings.insert_stripe()
            stripe_secret = stripe_secret.value
            stripe.api_key = stripe_secret
            token = request.form['stripeToken']
            try:
                charge = stripe.Charge.create(
                    amount=math.ceil(order_pay_amount * 100),
                    currency=order_currency.name.lower(),
                    description=description,
                    receipt_email=cart_instance.cart_details.email,
                    source=token,
                )
                if charge.status != "succeeded":
                    flash("Payment Wasn't Successful, Please Try A different card", "error")
                    return redirect(url_for('marketplace.order', step=3))
            except:
                flash("Payment Wasn't Successful, Please Try A different card", "error")
                return redirect(url_for('marketplace.order', step=3))
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
            return render_template('marketplace/cart/order_done.html', order=order_instance)
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
            return render_template('marketplace/cart/order_shipping.html', cart=cart_instance, form=form)

        elif step == 3:
            stripe_public = MSettings.query.filter_by(name='stripe_public').first()
            if not stripe_public:
                MSettings.insert_stripe()
            stripe_public = stripe_public.value
            if not cart_instance.cart_details:
                cart_instance.step = 2
                return redirect(url_for('marketplace.order', step=2))
            return render_template('marketplace/cart/order_payment.html', cart=cart_instance,
                                   stripe_public=stripe_public)

        return abort(404)
# Marketplace Shopping end


# Marketplace Seller Panel start
@marketplace.route('/seller-panel')
@login_required
@seller_required
def seller_panel():
    return render_template("marketplace/seller/index.html")


@marketplace.route('/seller-panel/stats')
@login_required
@seller_required
def seller_stats():
    orders_count = MSellerOrder.query.filter_by(seller=current_user).count()
    today_orders_count = MSellerOrder.query.filter_by(seller=current_user).filter(MSellerOrder.created_at.cast(Date)==datetime.datetime.now().date()).count()
    currencies = MCurrency.query.all()
    revenue = []
    for currency in currencies:
        orders = MSellerOrder.query.filter_by(seller=current_user).filter_by(currency=currency).all()
        print(len(orders), current_user.id)
        currency_sum = 0
        for order_instance in orders:
            currency_sum += order_instance.total_price
        revenue.append({'currency': currency, 'revenue': currency_sum})

    return render_template("marketplace/seller/stats.html", orders_count=orders_count, revenue=revenue, today_orders_count=today_orders_count)


@marketplace.route('/seller-panel/orders', defaults={'page': 1}, methods=['GET'])
@marketplace.route('/seller-panel/orders/<int:page>', methods=['GET'])
@login_required
@seller_required
def seller_orders(page):
    orders = MSellerOrder.query.filter_by(seller=current_user).paginate(page, per_page=50)
    orders_count = MSellerOrder.query.filter_by(seller=current_user).count()
    return render_template('marketplace/seller/orders/index.html', orders=orders, orders_count=orders_count)


@marketplace.route('/seller-panel/order/<int:order_id>/view', methods=['GET'])
@login_required
@seller_required
def seller_order_view(order_id):
    order_instance = MSellerOrder.query.get_or_404(order_id)
    return render_template('marketplace/seller/orders/order.html', order=order_instance)


@marketplace.route('/seller-panel/coupons', defaults={'page': 1}, methods=['GET'])
@marketplace.route('/seller-panel/coupons/<int:page>', methods=['GET'])
@login_required
@seller_required
def seller_coupons(page):
    return render_template('marketplace/seller/coupons/index.html')


@marketplace.route('/seller-panel/products', defaults={'page': 1}, methods=['GET'])
@marketplace.route('/seller-panel/products/<int:page>', methods=['GET'])
@login_required
@seller_required
def seller_products(page):
    products = MProduct.query.filter_by(seller_id=current_user.id).order_by(MProduct.created_at.asc()).paginate(page,
                                                                                                                per_page=50)
    products_count = MProduct.query.filter_by(seller_id=current_user.id).count()
    return render_template('marketplace/seller/products.html', products=products, products_count=products_count)


@marketplace.route('/seller-panel/products/add', methods=['GET', 'POST'])
@login_required
@seller_required
def seller_product_create():
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
                availability=form.availability.data,
                min_order_quantity=form.min_order_quantity.data,
                length=form.length.data,
                weight=form.weight.data,
                height=form.height.data,
                price=form.price.data,
                price_currency=form.price_currency.data,
                lead_time=form.lead_time.data,
            )
            db.session.add(prod)
            db.session.commit()
            flash('Product {} successfully created'.format(prod.name), 'success')
            return redirect(url_for('marketplace.seller_products'))
    return render_template('marketplace/seller/products-add-edit.html', form=form)


@marketplace.route('/seller-panel/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@seller_required
def seller_product_edit(product_id):
    product_instance = MProduct.query.filter_by(seller=current_user).filter_by(id=product_id).first_or_404()
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
            flash('Product {} successfully Updated'.format(product_instance.name), 'success')
            return redirect(url_for('marketplace.seller_products'))
    return render_template('marketplace/seller/products-add-edit.html', form=form, product=product_instance)


@marketplace.route('/seller-panel/products/<int:product_id>/_delete', methods=['POST'])
@login_required
@seller_required
def seller_product_delete(product_id):
    cat = MProduct.query.filter_by(seller=current_user).get_or_404(product_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Product.', 'success')
    return redirect(url_for('marketplace.seller_products'))


@marketplace.route('/seller-panel/shipping_methods', defaults={'page': 1}, methods=['GET'])
@marketplace.route('/seller-panel/shipping_methods/<int:page>', methods=['GET'])
@login_required
@seller_required
def marketplace_shipping_methods(page):
    shipping_methods = MShippingMethod.query.filter_by(seller=current_user).order_by(
        MShippingMethod.created_at.asc()).paginate(page, per_page=50)
    shipping_methods_count = MShippingMethod.query.filter_by(seller=current_user).count()
    return render_template('marketplace/seller/shipping_methods/index.html', shipping_methods=shipping_methods,
                           shipping_methods_count=shipping_methods_count)


@marketplace.route('/seller-panel/shipping_methods/add', methods=['GET', 'POST'])
@login_required
@seller_required
def marketplace_shipping_method_create():
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
            flash('Shipping Method {} successfully created'.format(shipping_method.name), 'success')
            return redirect(url_for('marketplace.marketplace_shipping_methods'))
    return render_template('marketplace/seller/shipping_methods/add-edit.html', form=form, currencies=currencies)


@marketplace.route('/seller-panel/shipping_methods/<int:shipping_method_id>/edit', methods=['GET', 'POST'])
@login_required
@seller_required
def marketplace_shipping_method_edit(shipping_method_id):
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
                return render_template('marketplace/seller/shipping_methods/add-edit.html', form=form,
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
            flash('Shipping Method {} successfully Updated'.format(shipping_method.name), 'success')
            return redirect(url_for('marketplace.marketplace_shipping_methods'))
    return render_template('marketplace/seller/shipping_methods/add-edit.html', form=form, currencies=currencies)


@marketplace.route('/seller-panel/shipping_methods/<int:shipping_method_id>/_delete', methods=['POST'])
@login_required
@seller_required
def marketplace_shipping_method_delete(shipping_method_id):
    cat = MShippingMethod.query.get_or_404(shipping_method_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Shipping Method.', 'success')
    return redirect(url_for('marketplace.marketplace_shipping_methods'))


@marketplace.route('/buyer-panel')
@buyer_required
def buyer_panel():
    return render_template("marketplace/buyer/index.html")


@marketplace.route('/anon-login', methods=['GET', 'POST'])
@anonymous_required
def anon_login():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash("Please provide a valid email", "error")
            return render_template("marketplace/buyer/anon_auth.html")
        user = User.query.filter_by(email=email).first()
        if user:
            flash("There is a mediville user with this email, please go to the login page instead", "error")
            return render_template("marketplace/buyer/anon_auth.html")
        orders_count = MOrder.query.filter_by(email=email).count()
        if orders_count == 0:
            flash("There is a no orders associated with this email on our database, please insert an email you made "
                  "orders with", "error")
            return render_template("marketplace/buyer/anon_auth.html")
        token = create_access_token(identity=request.form.get('email'), expires_delta=datetime.timedelta(hours=24))
        get_queue().enqueue(
            send_email,
            recipient=email,
            subject='You Have a new notification on Mediville',
            template='account/email/anon_auth',
            link=url_for('marketplace.anon_auth', token=token, _external=True),
            user=None
        )
        flash("Auth link were sent to {}".format(email), "success")
    return render_template("marketplace/buyer/anon_auth.html")


@marketplace.route('/anon-auth/<token>')
@anonymous_required
def anon_auth(token):
    try:
        token_decoded = decode_token(token)
    except:
        flash("Invalid or expired link", 'error')
        return redirect(url_for('marketplace.anon_login'))

    email = token_decoded['identity']
    new_token = create_access_token(identity=email, expires_delta=datetime.timedelta(days=30))
    resp = make_response(redirect(url_for('marketplace.buyer_panel')))
    resp.set_cookie('buyer_jwt', new_token)
    return resp


@marketplace.route('/buyer-panel/orders', defaults={'page': 1}, methods=['GET'])
@marketplace.route('/buyer-panel/orders/<int:page>', methods=['GET'])
@buyer_required
def buyer_orders(page):
    if current_user.is_authenticated:
        orders = MOrder.query.filter_by(buyer=current_user).paginate(page, per_page=50)
        orders_count = MOrder.query.filter_by(buyer=current_user).count()
    else:
        buyer_jwt = request.cookies.get('buyer_jwt')
        if not buyer_jwt:
            return redirect(url_for('marketplace.anon_login'))
        try:
            token_decoded = decode_token(buyer_jwt)
            email = token_decoded['identity']
            orders = MOrder.query.filter_by(email=email).paginate(page, per_page=50)
            orders_count = MOrder.query.filter_by(email=email).count()
        except:
            flash("Session expired authenticate again, please", 'error')
            return redirect(url_for('marketplace.anon_login'))
    return render_template('marketplace/buyer/orders/index.html', orders=orders, orders_count=orders_count)


@marketplace.route('/buyer-panel/order/<int:order_id>/view', methods=['GET'])
@buyer_required
def buyer_order_view(order_id):
    order_instance = MOrder.query.get_or_404(order_id)
    return render_template('marketplace/buyer/orders/order.html', order=order_instance)


# APIS
main_api.add_resource(AddToCart, '/add_to_cart')
main_api.add_resource(SubFromCart, '/sub_from_cart')
main_api.add_resource(CartCount, '/cart_count')
main_api.add_resource(OrderSummary, '/order_summary/<int:step>/<int:delivery>')
main_api.add_resource(ChangeOrderStatus, '/seller-panel/change_order_status')
