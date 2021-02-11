from datetime import datetime

from flask_login import login_required, current_user
from flask_restful import Resource, reqparse
from sqlalchemy import or_, and_

from app.models import User, Message
from app.utils import db, get_paginated_list, jsonify_object, strip_tags


class PostMessage(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('message', help='This field cannot be blank', required=True)

    @login_required
    def post(self, recipient_id):
        data = self.parser.parse_args()
        user = User.query.filter_by(id=recipient_id).first_or_404()
        msg = Message(user_id=current_user.id, recipient_id=recipient_id,
                      body=strip_tags(data['message']))
        db.session.add(msg)
        db.session.commit()
        db.session.refresh(msg)
        user.add_notification('unread_message', {'message': msg.id, 'count': user.new_messages()}, related_id=current_user.id, permanent=True)
        msg = Message.query.get(msg.id)
        return {
            'status': 1,
            'message': jsonify_object(msg)
        }


class GetMessages(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('first_page_last', required=False)

    @login_required
    def get(self, user_id, page_id):
        data = self.parser.parse_args()
        user = User.query.filter_by(id=user_id).first_or_404()
        for message in current_user.history(user.id):
            if message.recipient_id == current_user.id:
                message.read_at = db.func.now()
            db.session.add(message)
        db.session.commit()
        messages = Message.query.order_by(Message.timestamp.desc()). \
            filter(or_(and_(Message.recipient_id == user_id, Message.user_id == current_user.id),
                       and_(Message.recipient_id == current_user.id, Message.user_id == user_id)))
        if data['first_page_last']:
            messages = messages.filter(Message.id <= data['first_page_last'])
        messages = messages.paginate(page_id, per_page=20)
        messages = get_paginated_list(messages)
        return {
            'status': 1,
            'messages': messages,
            'now': str(datetime.now())
        }


class ToggleFollow(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user_id', help='This field cannot be blank', required=True)

    @login_required
    def post(self):
        data = self.parser.parse_args()
        user_id = data['user_id']
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            return {
                'status': 0,
                'message': "User Not Found"
            }
        if user == current_user:
            return {
                'status': 0,
                'message': "User Not Found"
            }
        if current_user in user.followers:
            current_user.unfollow(user)
            message = "You just un-followed {}".format(user.full_name)
            following = False
            db.session.commit()
        else:
            current_user.follow(user)
            message = "You just followed {}".format(user.full_name)
            following = True
            db.session.commit()
            n = user.add_notification('new_follower', {"count": current_user.new_followers() + 1},
                                      related_id=current_user.id,
                                      permanent=True)
        return {
            'status': 1,
            'message': message,
            'following': following
        }
