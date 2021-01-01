import json

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileAllowed
from wtforms import Flags

from app import db
from app.blueprints.admin.forms import MCategoryForm, MCurrencyForm, MShippingMethodForm, MProductForm
from app.blueprints.admin.views import admin
from app.decorators import admin_required
from app.models import User, Role, MCategory, MCurrency, MShippingMethod, MProduct, MSettings, MShippingMethodPrice, \
    MOrder

images = UploadSet('images', IMAGES)


@admin.route('/marketplace', methods=['GET'])
@login_required
@admin_required
def marketplace_index():
    return render_template('admin/marketplace/index.html')


@admin.route('/marketplace/sellers', defaults={'page': 1}, methods=['GET'])
@admin.route('/marketplace/sellers/<int:page>', methods=['GET'])
@login_required
@admin_required
def marketplace_sellers(page):
    users = User.query.filter_by(is_seller=True).paginate(page, per_page=50)
    users_count = User.query.filter_by(is_seller=True).count()
    roles = Role.query.all()
    return render_template('admin/marketplace/sellers/index.html', users=users, users_count=users_count, roles=roles)


@admin.route('/marketplace/categories', defaults={'page': 1}, methods=['GET'])
@admin.route('/marketplace/categories/<int:page>', methods=['GET'])
@login_required
@admin_required
def marketplace_categories(page):
    categories = MCategory.query.order_by(MCategory.created_at.asc()).paginate(page, per_page=50)
    categories_count = MCategory.query.count()
    return render_template('admin/marketplace/categories/index.html', categories=categories,
                           categories_count=categories_count)


@admin.route('/marketplace/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def marketplace_category_create():
    form = MCategoryForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image_filename = ""
            if request.files['image']:
                image_filename = images.save(request.files['image'])
            cat = MCategory(
                name=form.name.data,
                parent=form.parent.data,
                image=image_filename,
                is_featured=form.is_featured.data,
                order=form.order.data)
            db.session.add(cat)
            db.session.commit()
            flash('Category {} successfully created'.format(cat.name), 'success')
            return redirect(url_for('admin.marketplace_categories'))
    return render_template('admin/marketplace/categories/add-edit.html', form=form)


@admin.route('/marketplace/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def marketplace_category_edit(category_id):
    category = MCategory.query.get_or_404(category_id)
    form = MCategoryForm(obj=category)
    form.image.validators = [FileAllowed(images, 'Images only!')]
    form.image.flags = Flags()
    if request.method == 'POST':
        if form.validate_on_submit():
            image_filename = category.image
            if request.files['image']:
                image_filename = images.save(request.files['image'])
            category.name = form.name.data
            category.parent = form.parent.data
            category.image_filename = image_filename
            category.is_featured = form.is_featured.data
            category.order = form.order.data
            db.session.add(category)
            db.session.commit()
            flash('Category {} successfully Updated'.format(category.name), 'success')
            return redirect(url_for('admin.marketplace_categories'))
    return render_template('admin/marketplace/categories/add-edit.html', form=form, category=category)


@admin.route('/marketplace/categories/<int:category_id>/_delete', methods=['POST'])
@login_required
@admin_required
def marketplace_category_delete(category_id):
    cat = MCategory.query.get_or_404(category_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Category.', 'success')
    return redirect(url_for('admin.marketplace_categories'))


@admin.route('/marketplace/currencies', defaults={'page': 1}, methods=['GET'])
@admin.route('/marketplace/currencies/<int:page>', methods=['GET'])
@login_required
@admin_required
def marketplace_currencies(page):
    currencies = MCurrency.query.order_by(MCurrency.created_at.asc()).paginate(page, per_page=50)
    currencies_count = MCurrency.query.count()
    return render_template('admin/marketplace/currencies/index.html', currencies=currencies,
                           currencies_count=currencies_count)


@admin.route('/marketplace/currencies/add', methods=['GET', 'POST'])
@login_required
@admin_required
def marketplace_currency_create():
    form = MCurrencyForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.default.data:
                cats = MCurrency.query.all()
                for c in cats:
                    c.default = False
                    db.session.add(c)
            cat = MCurrency(
                name=form.name.data,
                default=form.default.data,
                symbol=form.symbol.data)
            db.session.add(cat)
            db.session.commit()
            flash('Currency {} successfully created'.format(cat.name), 'success')
            return redirect(url_for('admin.marketplace_currencies'))
    return render_template('admin/marketplace/currencies/add-edit.html', form=form)


@admin.route('/marketplace/currencies/<int:currency_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def marketplace_currency_edit(currency_id):
    currency = MCurrency.query.get_or_404(currency_id)
    form = MCurrencyForm(obj=currency)
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.default.data:
                cats = MCurrency.query.all()
                for c in cats:
                    c.default = False
                    db.session.add(c)
            currency.name = form.name.data
            currency.symbol = form.symbol.data
            currency.default = form.default.data
            db.session.add(currency)
            db.session.commit()
            flash('Currency {} successfully Updated'.format(currency.name), 'success')
            return redirect(url_for('admin.marketplace_currencies'))
    return render_template('admin/marketplace/currencies/add-edit.html', form=form)


@admin.route('/marketplace/currencies/<int:currency_id>/_delete', methods=['POST'])
@login_required
@admin_required
def marketplace_currency_delete(currency_id):
    cat = MCurrency.query.get_or_404(currency_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Currency.', 'success')
    return redirect(url_for('admin.marketplace_currencies'))


@admin.route('/marketplace/shipping_methods', defaults={'page': 1}, methods=['GET'])
@admin.route('/marketplace/shipping_methods/<int:page>', methods=['GET'])
@login_required
@admin_required
def marketplace_shipping_methods(page):
    shipping_methods = MShippingMethod.query.order_by(MShippingMethod.created_at.asc()).paginate(page, per_page=50)
    shipping_methods_count = MShippingMethod.query.count()
    return render_template('admin/marketplace/shipping_methods/index.html', shipping_methods=shipping_methods,
                           shipping_methods_count=shipping_methods_count)


@admin.route('/marketplace/shipping_methods/add', methods=['GET', 'POST'])
@login_required
@admin_required
def marketplace_shipping_method_create():
    form = MShippingMethodForm()
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
                return render_template('admin/marketplace/shipping_methods/add-edit.html', form=form,
                                       currencies=currencies)
            shipping_method = MShippingMethod(
                name=form.name.data,
                seller=form.seller.data
            )
            db.session.add(shipping_method)
            db.session.commit()
            db.session.refresh(shipping_method)
            for currency in currencies:
                input_field = 'price[{}]'.format(currency.id)
                shipping_method_price = MShippingMethodPrice(
                    shipping_method=shipping_method,
                    seller=form.seller.data,
                    price_currency=currency,
                    price=request.form.get(input_field)
                )
                db.session.add(shipping_method_price)
                db.session.commit()
            flash('Shipping Method {} successfully created'.format(shipping_method.name), 'success')
            return redirect(url_for('admin.marketplace_shipping_methods'))
    return render_template('admin/marketplace/shipping_methods/add-edit.html', form=form, currencies=currencies)


@admin.route('/marketplace/shipping_methods/<int:shipping_method_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def marketplace_shipping_method_edit(shipping_method_id):
    shipping_method = MShippingMethod.query.get_or_404(shipping_method_id)
    form = MShippingMethodForm(obj=shipping_method)
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
                return render_template('admin/marketplace/shipping_methods/add-edit.html', form=form,
                                       currencies=currencies)

            shipping_method.name = form.name.data
            shipping_method.seller = form.seller.data
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
                shipping_method_price.seller = form.seller.data
                shipping_method_price.price = request.form.get(input_field)
                db.session.add(shipping_method_price)
                db.session.commit()
            flash('Shipping Method {} successfully Updated'.format(shipping_method.name), 'success')
            return redirect(url_for('admin.marketplace_shipping_methods'))
    return render_template('admin/marketplace/shipping_methods/add-edit.html', form=form, currencies=currencies)


@admin.route('/marketplace/shipping_methods/<int:shipping_method_id>/_delete', methods=['POST'])
@login_required
@admin_required
def marketplace_shipping_method_delete(shipping_method_id):
    cat = MShippingMethod.query.get_or_404(shipping_method_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Shipping Method.', 'success')
    return redirect(url_for('admin.marketplace_shipping_methods'))


@admin.route('/marketplace/products', defaults={'page': 1}, methods=['GET'])
@admin.route('/marketplace/products/<int:page>', methods=['GET'])
@login_required
@admin_required
def marketplace_products(page):
    products = MProduct.query.order_by(MProduct.created_at.asc()).paginate(page, per_page=50)
    products_count = MProduct.query.count()
    return render_template('admin/marketplace/products/index.html', products=products, products_count=products_count)


@admin.route('/marketplace/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def marketplace_product_create():
    form = MProductForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image_filenames = []
            if request.files['images']:
                image_files = request.files.getlist('images')
                for image in image_files:
                    image_filename = images.save(image)
                    image_filenames.append(image_filename)
            image_filenames = json.dumps(image_filenames)
            cat = MProduct(
                name=form.name.data,
                images=image_filenames,
                description=form.description.data,
                is_featured=form.is_featured.data,
                seller=form.seller.data,
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
            db.session.add(cat)
            db.session.commit()
            flash('Product {} successfully created'.format(cat.name), 'success')
            return redirect(url_for('admin.marketplace_products'))
    return render_template('admin/marketplace/products/add-edit.html', form=form)


@admin.route('/marketplace/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def marketplace_product_edit(product_id):
    product = MProduct.query.get_or_404(product_id)
    form = MProductForm(obj=product)
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
            product.name = form.name.data
            product.is_featured = form.is_featured.data
            product.seller = form.seller.data
            product.images = image_filenames
            product.description = form.description.data
            product.categories = form.categories.data
            product.availability = form.availability.data
            product.min_order_quantity = form.min_order_quantity.data
            product.length = form.length.data
            product.weight = form.weight.data
            product.height = form.height.data
            product.price = form.price.data
            product.price_currency = form.price_currency.data
            product.lead_time = form.lead_time.data
            db.session.add(product)
            db.session.commit()
            flash('Product {} successfully Updated'.format(product.name), 'success')
            return redirect(url_for('admin.marketplace_products'))
    return render_template('admin/marketplace/products/add-edit.html', form=form, product=product)


@admin.route('/marketplace/products/<int:product_id>/_delete', methods=['POST'])
@login_required
@admin_required
def marketplace_product_delete(product_id):
    cat = MProduct.query.get_or_404(product_id)
    db.session.delete(cat)
    db.session.commit()
    flash('Successfully deleted Product.', 'success')
    return redirect(url_for('admin.marketplace_products'))


@admin.route('/marketplace/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def marketplace_settings():
    if request.method == 'POST':
        for i in request.form.lists():
            s = MSettings.query.filter_by(name=i[0]).first()
            if s:
                s.value = request.form.get(i[0])
                db.session.add(s)
                db.session.commit()
        flash("Changes saved successfully", "success")
        return redirect(url_for('admin.marketplace_settings'))
    c = MSettings.query.count()
    if c == 0:
        MSettings.insert_stripe()
    settings = MSettings.query.order_by(MSettings.id.asc()).all()
    return render_template('admin/marketplace/settings.html', settings=settings)


@admin.route('/marketplace/orders', defaults={'page': 1}, methods=['GET'])
@admin.route('/marketplace/orders/<int:page>', methods=['GET'])
@login_required
@admin_required
def marketplace_orders(page):
    orders = MOrder.query.order_by(MOrder.created_at.asc()).paginate(page, per_page=50)
    orders_count = MOrder.query.count()
    return render_template('admin/marketplace/orders/index.html', orders=orders, orders_count=orders_count)


@admin.route('/marketplace/order/<int:order_id>/view', methods=['GET'])
@login_required
@admin_required
def marketplace_order_view(order_id):
    order = MOrder.query.get_or_404(order_id)
    print(order.order_items_grouped())
    return render_template('admin/marketplace/orders/order.html', order=order)


@admin.route('/marketplace/coupons', defaults={'page': 1}, methods=['GET'])
@admin.route('/marketplace/coupons/<int:page>', methods=['GET'])
@login_required
@admin_required
def marketplace_coupons(page):
    return render_template('admin/marketplace/coupons/index.html')
