from app import db
from typing import List

class LandingSetting(db.Model):
    __tablename__ = 'landingsettings'

    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(128), unique=True)
    title = db.Column(db.String(128), unique=True)
    description = db.Column(db.String(180), unique=True)
    twitter_name = db.Column(db.String(25), unique=True)
    facebook_name = db.Column(db.String(25), unique=True)
    instagram_name = db.Column(db.String(25), unique=True)
    linkedin_name = db.Column(db.String(25), unique=True)
    tiktok_name = db.Column(db.String(25), unique=True)
    snap_chat_name = db.Column(db.String(25), unique=True)
    youtube = db.Column(db.String(25), unique=True)
    blog = db.Column(db.String(25), unique=True)
    about = db.Column(db.String(25), unique=True)
    contact = db.Column(db.String(25), unique=True)
    faq = db.Column(db.String(25), unique=True)
    #image_filename = db.Column(db.String, default=None, nullable=True)
    #image_url = db.Column(db.String, default=None, nullable=True)
    featured_title_one = db.Column(db.String(90), unique=True)
    featured_title_one_text = db.Column(db.String(180), unique=True)
    featured_title_one_icon = db.Column(db.String(25), unique=True)
    featured_title_two = db.Column(db.String(90), unique=True)
    featured_title_two_text = db.Column(db.String(180), unique=True)
    featured_title_two_icon = db.Column(db.String(25), unique=True)
    featured_title_three = db.Column(db.String(90), unique=True)
    featured_title_three_text = db.Column(db.String(180), unique=True)
    featured_title_three_icon = db.Column(db.String(25), unique=True)
    google_analytics_id = db.Column(db.String(25), unique=True)
    other_tracking_analytics_one = db.Column(db.Text)
    other_tracking_analytics_two = db.Column(db.Text)
    other_tracking_analytics_three = db.Column(db.Text)
    other_tracking_analytics_four = db.Column(db.Text)
    block_content_one = db.Column(db.Text)
    html_code_one = db.Column(db.Text)
    html_code_two = db.Column(db.Text)
    html_code_three = db.Column(db.Text)
    html_code_four = db.Column(db.Text)
    

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
    brand_url_five = db.Column(db.String(25), unique=True)


class TestDB(db.Model):
    __tablename__ = 'testdb'

    id = db.Column(db.Integer, primary_key=True)
    news_site_one_1 = db.Column(db.String(25), unique=True)
    news_site_twi_2 = db.Column(db.String(25), unique=True)
    
