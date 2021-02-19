from app import db
from typing import List

class LandingSetting(db.Model):
    __tablename__ = 'landing_settings'

    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(128), unique=True)
    title = db.Column(db.String(128), unique=True)
    description = db.Column(db.String(180), unique=True)
    twitter = db.Column(db.String(25), unique=True)
    facebook = db.Column(db.String(25), unique=True)
    instagram = db.Column(db.String(25), unique=True)
    linkedin = db.Column(db.String(25), unique=True)
    tiktok = db.Column(db.String(25), unique=True)
    snap_chat = db.Column(db.String(25), unique=True)
    youtube = db.Column(db.String(25), unique=True)
    google_analytics_id = db.Column(db.String(25), unique=True)
    other_tracking_analytics_one = db.Column(db.Text)
    other_tracking_analytics_two = db.Column(db.Text)
    other_tracking_analytics_three = db.Column(db.Text)
    other_tracking_analytics_four = db.Column(db.Text)     

class LandingImage(db.Model):
    __tablename__ = 'landingimages'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String, default=None, nullable=True)

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

class NewsLink(db.Model):
    __tablename__ = 'newslinks'

    id = db.Column(db.Integer, primary_key=True)
    news_site_one = db.Column(db.String(25), unique=True)
    news_site_two = db.Column(db.String(25), unique=True)
    news_site_three = db.Column(db.String(25), unique=True)
    news_site_four = db.Column(db.String(25), unique=True)
    news_site_five = db.Column(db.String(25), unique=True)
    news_url_one = db.Column(db.String(25), unique=True)
    news_url_two = db.Column(db.String(25), unique=True)
    news_url_three = db.Column(db.String(25), unique=True)
    news_url_four = db.Column(db.String(25), unique=True)
    brand_url_oo = db.Column(db.String(25), unique=True)


class TestDB(db.Model):
    __tablename__ = 'testdb'

    id = db.Column(db.Integer, primary_key=True)
    news_site_one_1 = db.Column(db.String(25), unique=True)
    news_site_twi_2 = db.Column(db.String(25), unique=True)
    
