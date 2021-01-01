from flask import session, render_template
from flask_login import current_user
from flask_restful import Resource, reqparse

from app.decorators import seller_required
from app.models import User, MCart, MProduct, MShippingMethod, MCartItem, MSellerCart, MSellerOrder, MOrderStatusChange
from app.utils import jsonify_object, db


def get_current_cart():
    session_id = session['cart_id']
    if current_user.is_authenticated:
        cart = MCart.query.filter_by(user_id=current_user.id).first()
        if cart:
            MCart.query.filter_by(user_id=current_user.id).filter(MCart.id != cart.id).delete()
        else:
            cart = MCart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
            db.session.refresh(cart)
    else:
        cart = MCart.query.filter_by(session_id=session_id).first()
        if cart:
            MCart.query.filter_by(session_id=session_id).filter(MCart.id != cart.id).delete()
        else:
            cart = MCart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()
            db.session.refresh(cart)

    return cart


class CartCount(Resource):
    def get(self):
        cart = get_current_cart()
        return {
            'status': 1,
            'count': len(cart.cart_items)
        }


class OrderSummary(Resource):
    def get(self, step, delivery):
        cart = get_current_cart()
        delivery = MShippingMethod.query.filter_by(id=delivery).first()
        return render_template('marketplace/cart/order_summary.html', step=step, cart=cart, delivery=delivery)


class AddToCart(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('product_id', help='This field cannot be blank', required=True)

    def post(self):
        data = self.parser.parse_args()
        product = MProduct.query.get(data['product_id'])
        if not product:
            return {
                'status': 0,
                'title': "Error",
                'message': "Couldn't find product to add"
            }
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
        cart = get_current_cart()
        cart_currency = cart.currency
        if cart_currency:
            if cart_currency != product.price_currency:
                return {
                    'status': 0,
                    'title': "Error",
                    'message': "Cannot add product of currency {} because cart currency is {}".format(
                        product.price_currency.name, cart_currency.name)
                }
        cart.user_id = user_id
        seller_cart = MSellerCart.query.filter_by(cart=cart).filter_by(seller=product.seller).first()
        if not seller_cart:
            seller_cart = MSellerCart(
                cart=cart,
                seller=product.seller,
                currency=product.price_currency,
                buyer=current_user if current_user.is_authenticated else None,
            )
        db.session.add(seller_cart)
        db.session.commit()
        db.session.refresh(seller_cart)
        cart_item = MCartItem.query.filter_by(product=product).filter_by(cart=cart).first()
        if cart_item:
            cart_item.count += 1
        else:
            cart_item = MCartItem(
                cart=cart,
                seller_cart=seller_cart,
                product=product,
                seller=product.seller,
                buyer=current_user if current_user.is_authenticated else None,
                count=1
            )
        db.session.add(cart)
        db.session.add(cart_item)
        db.session.commit()
        count = cart.product_count(product.id)
        return {
            'status': 1,
            'title': "Cart Change",
            'message': "{} pieces of {} are in the cart now".format(product.name, count),
            'count': count
        }


class SubFromCart(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('product_id', help='This field cannot be blank', required=True)

    def post(self):
        data = self.parser.parse_args()
        product = MProduct.query.get(data['product_id'])
        if not product:
            return {
                'status': 0,
                'title': "Error",
                'message': "Couldn't find product to add"
            }
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
        cart = get_current_cart()
        cart.user_id = user_id
        cart_item = MCartItem.query.filter_by(product=product).filter_by(cart=cart).first()
        if cart_item:
            cart_item_seller = cart_item.seller
            if cart_item.count > 1:
                cart_item.count -= 1
                db.session.add(cart_item)
            else:
                db.session.delete(cart_item)
            seller_cart = MSellerCart.query.filter_by(cart=cart, seller=cart_item_seller).first()
            if seller_cart:
                if len(seller_cart.cart_items) < 1:
                    db.session.delete(seller_cart)
        db.session.commit()
        count = cart.product_count(product.id)
        return {
            'status': 1,
            'title': "Cart Change",
            'message': "Item Removed From Cart Successfully : {}".format(count),
            'count': count
        }


class ChangeOrderStatus(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('order_id', help='This field cannot be blank', required=True)

    @seller_required
    def post(self):
        data = self.parser.parse_args()
        order = MSellerOrder.query.filter_by(seller=current_user).filter_by(id=data['order_id']).first()
        if not order:
            return {
                'status': 0,
                'title': "Error",
                'message': "Couldn't find this order"
            }
        if order.next_action:
            current_status = order.order_status
            next_action = order.next_action
            order.order_status = next_action[0]
            status_change = MOrderStatusChange(
                order=order.order,
                seller_order=order,
                changed_from=current_status,
                changed_to=next_action[0]
            )
            db.session.add(order)
            db.session.add(status_change)
            db.session.commit()
            next_status = False
            next_label = False
            if order.next_action:
                next_status = order.next_action[0]
                next_label = order.next_action[1]
            return {
                'status': 1,
                'title': "Status Change",
                'message': "Order {} Status changed to {} Successfully".format(order.order.order_number,
                                                                               next_action[1]),
                'current_status': next_action[1],
                'next_status': next_status,
                'next_label': next_label
            }
        return {
            'status': 0,
            'title': "Error",
            'message': "Unknown error happened"
        }
