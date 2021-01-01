import json
import time

from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, query_expression

from app import whooshee
#from flask_whooshee import Whooshee
from app.utils import db, random_char


class MCategory(db.Model):
    __tablename__ = 'marketplace_categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('marketplace_categories.id', ondelete="CASCADE"), nullable=True,
                          default=None)
    name = db.Column(db.String(), default=None, nullable=False)
    image = db.Column(db.String(), default=None, nullable=False)
    order = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    parent = db.relationship("MCategory", remote_side=[id])
    children = db.relationship("MCategory")


class MCurrency(db.Model):
    __tablename__ = 'marketplace_currency'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), default=None, nullable=False)
    symbol = db.Column(db.String())
    default = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class MShippingMethod(db.Model):
    __tablename__ = 'marketplace_shipping_methods'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), default=None, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    seller = db.relationship("User", backref="shipping_methods")

    def get_price(self, currency, seller):
        price = None
        shipping_method_price = MShippingMethodPrice.query.filter_by(shipping_method=self).filter_by(price_currency=currency).filter_by(seller=seller).first()
        if shipping_method_price:
            price = shipping_method_price.price
        return price


class MShippingMethodPrice(db.Model):
    __tablename__ = 'marketplace_shipping_method_prices'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shipping_method_id = db.Column(db.Integer, db.ForeignKey('marketplace_shipping_methods.id', ondelete="CASCADE"))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), default=None, nullable=True)
    price_currency_id = db.Column(db.Integer, db.ForeignKey('marketplace_currency.id', ondelete="CASCADE"))
    price = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    seller = db.relationship("User", backref="shipping_methods_prices")
    shipping_method = db.relationship("MShippingMethod", backref="prices")
    price_currency = db.relationship("MCurrency")


class MProductCategory(db.Model):
    __tablename__ = 'marketplace_product_categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('marketplace_categories.id', ondelete="CASCADE"))
    product_id = db.Column(db.Integer, db.ForeignKey('marketplace_products.id', ondelete="CASCADE"))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


@whooshee.register_model('name', 'description')
class MProduct(db.Model):
    __tablename__ = 'marketplace_products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    images = db.Column(db.Text)
    description = db.Column(db.String())
    availability = db.Column(db.Boolean, default=True)
    min_order_quantity = db.Column(db.Integer, default=1)
    length = db.Column(db.Float)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    price = db.Column(db.Float)
    price_currency_id = db.Column(db.Integer, db.ForeignKey('marketplace_currency.id', ondelete="CASCADE"))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    is_featured = db.Column(db.Boolean, default=False)
    lead_time = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    categories = db.relationship("MCategory", secondary='marketplace_product_categories',
                                 backref=backref("products"),
                                 primaryjoin=(MProductCategory.product_id == id),
                                 secondaryjoin=(MProductCategory.category_id == MCategory.id))

    price_currency = db.relationship("MCurrency")
    seller = db.relationship("User", backref="products")
    score = query_expression()

    @property
    def image_items(self):
        return [url_for('_uploads.uploaded_file', setname='images',
                        filename=image, _external=True) for image in json.loads(self.images)]


class MCart(db.Model):
    __tablename__ = 'marketplace_carts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=True, default=None)
    step = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    user = db.relationship("User", backref="cart")
    cart_details = db.relationship("MCartDetails", uselist=False, back_populates="cart")

    @property
    def products_count(self):
        return len(self.products())

    @property
    def currency(self):
        if len(self.cart_items) > 0:
            first_product = self.cart_items[0].product
            return first_product.price_currency
        return None

    def product_count(self, product_id):
        product = MProduct.query.get(product_id)
        if product:
            cart_item = MCartItem.query.filter_by(cart=self).filter_by(product=product).first()
            if cart_item:
                return cart_item.count
        return 0

    def products(self):
        prods = []
        for cart_item in self.cart_items:
            prods.append({'product_id': cart_item.product_id, 'count': cart_item.count, 'object': cart_item.product})

        return prods

    def sellers(self):
        sellers = []
        for cart_item in self.cart_items:
            if cart_item.seller not in sellers:
                sellers.append(cart_item.seller)
        return sellers

    def orders(self):
        orders = []
        for seller in self.sellers():
            items = MCartItem.query.filter_by(seller=seller).filter_by(cart=self).all()
            prods = []
            for cart_item in items:
                prods.append(
                    {'product_id': cart_item.product_id, 'count': cart_item.count, 'object': cart_item.product})
            seller_cart = MSellerCart.query.filter_by(cart=self).filter_by(seller=seller).first()
            shipping = None
            if seller_cart:
                shipping = seller_cart.shipping_method
            orders.append({'seller': seller, 'items': prods, 'shipping': shipping})
        return orders

    @property
    def products_total(self):
        sum = 0
        for order in self.orders():
            for prod in order['items']:
                sum += prod['object'].price * prod['count']
        return sum

    def price_paid(self):
        sum = 0
        for order in self.orders():
            for prod in order['items']:
                sum += prod['object'].price * prod['count']
            if order['shipping']:
                sum += order['shipping'].get_price(self.currency, order['seller'])
        return sum

    def price_shipping(self):
        sum = 0
        for order in self.orders():
            if order['shipping']:
                sum += order['shipping'].get_price(self.currency, order['seller'])
        return sum

    def generate_order_number(self):
        if self.user_id is not None:
            user_part = str(self.user_id)
        else:
            user_part = self.session_id[:4]
        return random_char(4) + user_part + hex(int(time.time()))


class MSellerCart(db.Model):
    __tablename__ = 'marketplace_seller_carts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('marketplace_carts.id', ondelete="CASCADE"))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    shipping_method_id = db.Column(db.Integer, db.ForeignKey('marketplace_shipping_methods.id', ondelete="CASCADE"),
                                   nullable=True, default=None)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=True, default=None)
    current_currency_id = db.Column(db.Integer, db.ForeignKey('marketplace_currency.id', ondelete="CASCADE"))

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    cart = db.relationship("MCart", backref="seller_carts")
    seller = db.relationship("User", backref="seller_carts_active", primaryjoin="User.id == MSellerCart.seller_id")
    buyer = db.relationship("User", backref="my_seller_carts", primaryjoin="User.id == MSellerCart.buyer_id")
    currency = db.relationship("MCurrency")
    shipping_method = db.relationship("MShippingMethod", backref="seller_cart_shipping")


class MCartItem(db.Model):
    __tablename__ = 'marketplace_cart_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('marketplace_carts.id', ondelete="CASCADE"), nullable=True,
                        default=None)
    seller_cart_id = db.Column(db.Integer, db.ForeignKey('marketplace_seller_carts.id', ondelete="CASCADE"), nullable=True,
                        default=None)
    product_id = db.Column(db.Integer, db.ForeignKey('marketplace_products.id', ondelete="CASCADE"))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=True, default=None)
    count = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    cart = db.relationship("MCart", backref=backref("cart_items", lazy='joined'))
    seller_cart = db.relationship("MSellerCart", backref="cart_items")
    seller = db.relationship("User", backref="items_in_cart", primaryjoin="User.id == MCartItem.seller_id")
    buyer = db.relationship("User", backref="my_cart_items", primaryjoin="User.id == MCartItem.buyer_id")
    product = db.relationship("MProduct", backref="product_cart_items")


class MCartDetails(db.Model):
    __tablename__ = 'marketplace_cart_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('marketplace_carts.id', ondelete="CASCADE"), nullable=True,
                        default=None)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    mobile_phone = db.Column(db.BigInteger, unique=True, index=True)
    zip = db.Column(db.String(10), index=True)
    city = db.Column(db.String(64), index=True)
    state = db.Column(db.String(64), index=True)
    country = db.Column(db.String(64), index=True)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    cart = db.relationship("MCart", uselist=False, back_populates="cart_details")


class MSettings(db.Model):
    __tablename__ = 'marketplace_settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String())
    display_name = db.Column(db.String())
    value = db.Column(db.String(), default=None)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    @staticmethod
    def insert_stripe():
        settings = [
            ['stripe_public', 'Stripe Public Key'],
            ['stripe_secret', 'Stripe Secret Key']
        ]
        for s in settings:
            setting = MSettings.query.filter_by(name=s[0]).first()
            if setting is None:
                setting = MSettings(name=s[0], display_name=s[1])
            db.session.add(setting)
        db.session.commit()


class MOrder(db.Model):
    __tablename__ = 'marketplace_orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String())
    charge_id = db.Column(db.String(), default=None, nullable=True)
    order_status = db.Column(db.Integer, default=0)
    products_total = db.Column(db.Float, default=0)
    shipping_cost = db.Column(db.Float, default=0)
    order_total = db.Column(db.Float, default=0)
    order_discount = db.Column(db.Float, default=0)
    order_pay_amount = db.Column(db.Float, default=0)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    price_currency_id = db.Column(db.Integer, db.ForeignKey('marketplace_currency.id', ondelete="CASCADE"))
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), index=True)
    mobile_phone = db.Column(db.BigInteger, index=True)
    zip = db.Column(db.String(10), index=True)
    city = db.Column(db.String(64), index=True)
    state = db.Column(db.String(64), index=True)
    country = db.Column(db.String(64), index=True)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    buyer = db.relationship("User", backref="orders")
    price_currency = db.relationship("MCurrency")

    @property
    def order_status_explained(self):
        if self.order_status == 0:
            return 'Pending'
        return self.order_status

    @hybrid_property
    def full_name(self):
        if self.buyer:
            return self.buyer.full_name
        first = ''
        last = ''
        if self.first_name:
            first = self.first_name
        if self.last_name:
            last = self.last_name
        return first + " " + last

    @property
    def sellers(self):
        sellers = []
        for seller_order in self.order_seller_orders:
            if seller_order.seller not in sellers:
                sellers.append(seller_order.seller)
        return sellers

    def order_items_grouped(self):
        orders = []
        for seller_order in self.order_seller_orders:
            items = MOrderItem.query.filter_by(seller_order=seller_order).filter_by(order=self).all()
            orders.append({'seller': seller_order.seller, 'items': items, 'shipping': seller_order.shipping_method})
        return orders


class MSellerOrder(db.Model):
    __tablename__ = 'marketplace_seller_orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('marketplace_orders.id', ondelete="CASCADE"))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    order_status = db.Column(db.Integer, default=0)
    shipping_method_id = db.Column(db.Integer, db.ForeignKey('marketplace_shipping_methods.id', ondelete="CASCADE"),
                                   nullable=True, default=None)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    current_currency_id = db.Column(db.Integer, db.ForeignKey('marketplace_currency.id', ondelete="CASCADE"))
    shipping_cost = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    order = db.relationship("MOrder", backref="order_seller_orders")
    seller = db.relationship("User", backref="seller_orders_sold", primaryjoin="User.id == MSellerOrder.seller_id")
    buyer = db.relationship("User", backref="seller_orders_bought", primaryjoin="User.id == MSellerOrder.buyer_id")
    currency = db.relationship("MCurrency")
    shipping_method = db.relationship("MShippingMethod", backref="seller_order_shipping")

    @property
    def order_status_explained(self):
        if self.order_status == 0:
            return 'Pending'
        elif self.order_status == 1:
            return 'Received'
        elif self.order_status == 2:
            return 'Processing'
        elif self.order_status == 3:
            return "Shipping"
        elif self.order_status == 4:
            return "Completed"
        return self.order_status

    @property
    def next_action(self):
        if self.order_status == 0:
            return 1, 'Received'
        elif self.order_status == 1:
            return 2, "Processing"
        elif self.order_status == 2:
            return 3, "Shipping"
        elif self.order_status == 3:
            return 4, "Completed"

        return False

    @property
    def product_total(self):
        sum = 0
        for item in self.order_items:
            sum += item.current_total_price
        return sum

    @property
    def total_price(self):
        return self.product_total + self.shipping_cost


class MOrderItem(db.Model):
    __tablename__ = 'marketplace_order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('marketplace_orders.id', ondelete="CASCADE"), nullable=True,
                         default=None)
    seller_order_id = db.Column(db.Integer, db.ForeignKey('marketplace_seller_orders.id', ondelete="CASCADE"), nullable=True,
                         default=None)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    product_id = db.Column(db.Integer, db.ForeignKey('marketplace_products.id', ondelete="CASCADE"))
    count = db.Column(db.Integer, default=1)
    current_price = db.Column(db.Float, default=0)
    current_total_price = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    order = db.relationship("MOrder", backref="order_items")
    seller_order = db.relationship("MSellerOrder", backref="order_items")
    seller = db.relationship("User", backref="orders_sold", primaryjoin="User.id == MOrderItem.seller_id")
    buyer = db.relationship("User", backref="orders_bought", primaryjoin="User.id == MOrderItem.buyer_id")
    product = db.relationship("MProduct", backref="product_orders")


class MOrderStatusChange(db.Model):
    __tablename__ = 'marketplace_order_status_changes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('marketplace_orders.id', ondelete="CASCADE"), nullable=True,
                         default=None)
    seller_order_id = db.Column(db.Integer, db.ForeignKey('marketplace_seller_orders.id', ondelete="CASCADE"), nullable=True,
                                default=None)
    changed_from = db.Column(db.Integer, default=0)
    changed_to = db.Column(db.Integer, default=0)

    order = db.relationship("MOrder", backref="order_statuses")
    seller_order = db.relationship("MSellerOrder", backref="order_status_changes")

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    @property
    def order_status_explained(self):
        if self.changed_to == 0:
            return 'Pending', 'Your Order is still pending', ''
        elif self.changed_to == 1:
            return 'Received', 'The seller received your order', 'envelope open outline'
        elif self.changed_to == 2:
            return 'Processing', 'The seller is working on your order now', 'spinner'
        elif self.changed_to == 3:
            return "Shipping", 'Your Order is on the way to you', 'truck'
        elif self.changed_to == 4:
            return "Completed", 'Order Delivered', 'thumbs up'
        return self.changed_to
