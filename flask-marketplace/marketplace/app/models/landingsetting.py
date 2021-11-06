from app import db
from typing import List

class LandingSetting(db.Model):
    __tablename__ = 'landing_settings'

    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(150), unique=True)
    company_name = db.Column(db.String(250), unique=True)
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(50))
    location = db.Column(db.String(250))
    title = db.Column(db.String(180), unique=True)
    description = db.Column(db.Text)
    twitter = db.Column(db.String(150), unique=True)
    facebook = db.Column(db.String(150), unique=True)
    instagram = db.Column(db.String(150), unique=True)
    linkedin = db.Column(db.String(150), unique=True)
    tiktok = db.Column(db.String(150), unique=True)
    snap_chat = db.Column(db.String(150), unique=True)
    youtube = db.Column(db.String(150), unique=True)
    google_analytics_id = db.Column(db.String(250), unique=True)
    other_tracking_analytics_one = db.Column(db.Text)
    other_tracking_analytics_two = db.Column(db.Text)
    other_tracking_analytics_three = db.Column(db.Text)
    other_tracking_analytics_four = db.Column(db.Text)     

class LandingImage(db.Model):
    __tablename__ = 'landingimages'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, default=None, nullable=True)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images', filename=self.image, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.image)

class OurBrand(db.Model):
    __tablename__ = 'ourbrands'

    id = db.Column(db.Integer, primary_key=True)
    brand_name_one = db.Column(db.String(25), unique=True)
    brand_name_two = db.Column(db.String(25), unique=True)
    brand_name_three = db.Column(db.String(25), unique=True)
    brand_name_four = db.Column(db.String(25), unique=True)
    brand_name_five = db.Column(db.String(25), unique=True)
    brand_url_one = db.Column(db.String(25), unique=True)
    brand_url_two = db.Column(db.String(25), unique=True)
    brand_url_three = db.Column(db.String(25), unique=True)
    brand_url_four = db.Column(db.String(25), unique=True)
    brand_url_five = db.Column(db.String(25), unique=True)



class Feature(db.Model):
    __tablename__ = "feature"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=True)
    description = db.Column(db.String(250), nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    
