from sqlalchemy_mptt import BaseNestedSets

from app.utils import db
from sqlalchemy.orm import backref


class BlogCategory(db.Model):
    __tablename__ = 'blog_categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), default=None, nullable=False)
    order = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class BlogTag(db.Model):
    __tablename__ = 'blog_tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), default=None, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class BlogPostCategory(db.Model):
    __tablename__ = 'blog_post_categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id', ondelete="CASCADE"))
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id', ondelete="CASCADE"))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class BlogPostTag(db.Model):
    __tablename__ = 'blog_post_tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('blog_tags.id', ondelete="CASCADE"))
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id', ondelete="CASCADE"))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    image = db.Column(db.String(), default=None, nullable=False)
    text = db.Column(db.Text(), default=None)
    comments = db.relationship('BlogComment', backref=backref('post'), lazy='dynamic',
                               cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    creator = db.relationship('User')
    categories = db.relationship("BlogCategory", secondary='blog_post_categories',
                                 backref=backref("posts"),
                                 primaryjoin=(BlogPostCategory.post_id == id),
                                 secondaryjoin=(BlogPostCategory.category_id == BlogCategory.id))
    tags = db.relationship("BlogTag", secondary='blog_post_tags',
                                 backref=backref("posts"),
                                 primaryjoin=(BlogPostTag.post_id == id),
                                 secondaryjoin=(BlogPostTag.tag_id == BlogTag.id))

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class BlogComment(db.Model, BaseNestedSets):
    __tablename__ = 'blog_post_comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(), default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id', ondelete="CASCADE"))
    author = db.relationship('User')
    depth = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __init__(self, post_id, user_id, text, parent_id=None):
        self.post_id = post_id
        self.user_id = user_id
        self.text = text
        self.parent_id = parent_id


class BlogNewsLetter(db.Model):
    __tablename__ = 'blog_news_letters'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), default=None, nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
