from app import db
import json
import time

from flask import url_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, query_expression
from sqlalchemy.sql import func


class SiteLogo(db.Model):
    _tablename_ = "logo"
    id = db.Column(db.Integer, primary_key=True)
    logo_image = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images', filename=self.logo_image, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.logo_image)

class BackgroundImage(db.Model):
    _tablename_ = "background_image"
    id = db.Column(db.Integer, primary_key=True)
    background_image = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images', filename=self.background_image, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.background_image)