from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from app.models import EditableHTML, BackgroundImage, ContactMessage, LandingSetting, OurBrand, User, MCategory, MProduct, MSettings, MBrand, MBanner, SiteLogo, BackgroundImage, MCurrency
from app.blueprints.marketplace.forms import SearchForm

seo_world = Blueprint('seo_world', __name__)

ROWS_PER_PAGE = 5


@seo_world.route('/<keywordone>-<keywordtwo>-in-<location>')
def data_location(keywordone, keywordtwo, location):
    form = SearchForm()
    banner = MBanner.query.first()
    background = BackgroundImage.query.first()
    logo = SiteLogo.query.first()
    settings = LandingSetting.query.first()
    website_settings = MSettings.query.first()
    brands = MBrand.query.order_by(MBrand.created_at.asc()).limit(5).all()
    featured_products = MProduct.query.filter_by(availability=True).filter_by(
        is_featured=True).order_by(MProduct.created_at.asc()).limit(4).all()  # .limit(5).all()
    new_arrived_products = MProduct.query.filter_by(
        availability=True).order_by(MProduct.created_at.desc()).limit(4).all()
    featured_categories = MCategory.query.filter_by(is_featured=True).all()
    categories = MCategory.query.limit(6).all()
    #products = MProduct.query.limit(6).all()

    products_count = MProduct.query.count()
    page = request.args.get('page', 1, type=int)
    products = MProduct.query.paginate(page, per_page=ROWS_PER_PAGE)
    return render_template('seo/page-listing-large.html', keywordone=keywordone, keywordtwo=keywordtwo, location=location, form=form, featured_categories=featured_categories, categories=categories, featured_products=featured_products,
                           new_arrived_products=new_arrived_products, settings=settings, website_settings=website_settings, brands=brands, banner=banner,
                           logo=logo, products=products, background=background, products_count=products_count)#, product_pagination=product_pagination)



