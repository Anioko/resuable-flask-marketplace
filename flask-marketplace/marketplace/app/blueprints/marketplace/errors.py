from flask import render_template
from app.models import LandingSetting
from app.blueprints.marketplace.views import marketplace
from app.blueprints.marketplace.forms import ReviewForm, SearchForm


@marketplace.app_errorhandler(403)
def forbidden(_):
    form = SearchForm()
    banner = MBanner.query.first()
    background = BackgroundImage.query.first()
    logo = SiteLogo.query.first()
    settings = LandingSetting.query.all()
    website_settings = MSettings.query.first()
    return render_template('errors/403.html', form=form, settings=settings, website_settings=website_settings, background=background, logo=logo), 403


@marketplace.app_errorhandler(404)
def page_not_found(_):
    form = SearchForm()
    banner = MBanner.query.first()
    background = BackgroundImage.query.first()
    logo = SiteLogo.query.first()
    settings = LandingSetting.query.all()
    website_settings = MSettings.query.first()
    return render_template('errors/404.html', form=form, settings=settings, website_settings=website_settings, background=background, logo=logo), 404


@marketplace.app_errorhandler(500)
def internal_server_error(_):
    form = SearchForm()
    banner = MBanner.query.first()
    background = BackgroundImage.query.first()
    logo = SiteLogo.query.first()
    settings = LandingSetting.query.all()
    website_settings = MSettings.query.first()
    return render_template('errors/500.html', form=form, settings=settings, website_settings=website_settings, background=background, logo=logo), 500



