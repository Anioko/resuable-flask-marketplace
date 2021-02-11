import operator
import operator
import os
import uuid
from functools import partial
from hashlib import md5, sha512

from flask import Flask, session, request
from flask.globals import _lookup_req_object
from flask_assets import Environment
from flask_ckeditor import CKEditor
from flask_compress import Compress
from flask_jwt_extended import JWTManager
from flask_login._compat import text_type
from flask_login.utils import _get_remote_addr
from flask_mail import Mail
from flask_moment import Moment
from flask_rq import RQ
from flask_share import Share
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import CSRFProtect

# from app.blueprints.api.views import main_api
from werkzeug.local import LocalProxy

from app.utils import db, login_manager, get_cart, image_size, json_load
from config import config
from .assets import app_css, app_js, vendor_css, vendor_js
from flask_session import Session
from flask_whooshee import Whooshee

# from app.models import Notification

basedir = os.path.abspath(os.path.dirname(__file__))

mail = Mail()
csrf = CSRFProtect()
compress = Compress()
images = UploadSet('images', IMAGES)
docs = UploadSet('docs', ('rtf', 'odf', 'ods', 'gnumeric', 'abw', 'doc', 'docx', 'xls', 'xlsx', 'pdf'))
share = Share()
moment = Moment()
jwt = JWTManager()
sess = Session()
whooshee = Whooshee()
# Set up Flask-Login
login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'

import app.models as models


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # not using sqlalchemy event system, hence disabling it
    app.config['UPLOADED_IMAGES_DEST'] = 'C:/Users/oem/Desktop/marketplace/marketplace/app/static/frontend/images/' if \
        not os.environ.get('UPLOADED_IMAGES_DEST') else os.path.dirname(os.path.realpath(__file__)) + os.environ.get(
        'UPLOADED_IMAGES_DEST')
    app.config['UPLOADED_DOCS_DEST'] = ':/Users/oem/Desktop/marketplace/marketplace/appstatic/docs/' if \
        not os.environ.get('UPLOADED_DOCS_DEST') else os.path.dirname(os.path.realpath(__file__)) + os.environ.get(
        'UPLOADED_DOCS_DEST')
    app.config['docs'] = app.config['UPLOADED_DOCS_DEST']

    app.config['CKEDITOR_SERVE_LOCAL'] = True
    app.config['CKEDITOR_HEIGHT'] = 400
    app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
    app.config['CKEDITOR_ENABLE_CSRF'] = True  # if you want to enable CSRF protect, uncomment this line
    app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')
    #app.config['WHOOSH_BASE']='whoosh'

    config[config_name].init_app(app)

    # Set up extensions
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    compress.init_app(app)
    RQ(app)
    configure_uploads(app, (images))
    configure_uploads(app, docs)
    ckeditor = CKEditor(app)
    share.init_app(app)
    moment.init_app(app)
    jwt.init_app(app)
    sess.init_app(app)
    #whooshee.init_app(app)
    whooshee = Whooshee(app)
    # Register Jinja template functions
    from .utils import register_template_utils
    register_template_utils(app)

    # Set up asset pipeline
    assets_env = Environment(app)
    dirs = ['assets/styles', 'assets/scripts']
    for path in dirs:
        assets_env.append_path(os.path.join(basedir, path))
    assets_env.url_expire = True

    assets_env.register('app_css', app_css)
    assets_env.register('app_js', app_js)
    assets_env.register('vendor_css', vendor_css)
    assets_env.register('vendor_js', vendor_js)

    # Configure SSL if platform supports it
    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        SSLify(app)

    # Create app blueprints
    from .blueprints.public import public as public_blueprint
    app.register_blueprint(public_blueprint)

    from .blueprints.seo_world import seo_world as seo_world_blueprint
    app.register_blueprint(seo_world_blueprint)

    from .blueprints.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .blueprints.account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')

    from .blueprints.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .blueprints.marketplace import marketplace as marketplace_blueprint
    app.register_blueprint(marketplace_blueprint, url_prefix='/marketplace')

    from .blueprints.organisations import organisations as organisations_blueprint
    app.register_blueprint(organisations_blueprint, url_prefix='/organisations')

    from .blueprints.sitemaps import sitemaps as sitemaps_blueprint
    app.register_blueprint(sitemaps_blueprint)

    from .blueprints.api import api as apis_blueprint
    app.register_blueprint(apis_blueprint, url_prefix='/api')

    # main_api.init_app(app)
    app.jinja_env.globals.update(json_load=json_load, image_size=image_size, get_cart=get_cart)

    @app.before_request
    def before_request():
        try:
            session['cart_id']
        except:
            u = uuid.uuid4()
            user_agent = request.headers.get('User-Agent')
            if user_agent is not None:
                user_agent = user_agent.encode('utf-8')
            base = 'cart: {0}|{1}|{2}'.format(_get_remote_addr(), user_agent, u)
            if str is bytes:
                base = text_type(base, 'utf-8', errors='replace')  # pragma: no cover
            h = sha512()
            h.update(base.encode('utf8'))
            session['cart_id'] = h.hexdigest()
    
    @app.cli.command()
    def reindex():
        with app.app_context():
            whooshee.reindex()
            
    @app.cli.command()
    def routes():
        """'Display registered routes"""
        rules = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            rules.append((rule.endpoint, methods, str(rule)))

        sort_by_rule = operator.itemgetter(2)
        for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
            route = '{:50s} {:25s} {}'.format(endpoint, methods, rule)
            print(route)


    @app.template_filter('product')
    def product(o):
        """check if object is user"""
        from app.models import MProduct
        return o.__class__ == MProduct
    
    return app
