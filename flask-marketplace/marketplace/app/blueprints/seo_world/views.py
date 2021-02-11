from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from app.models import MSettings

seo_world = Blueprint('seo_world', __name__)



@seo_world.route('/<keywordone>-<keywordtwo>-in-<location>')
def data_location(keywordone, keywordtwo, location):
    website_settings = MSettings.query.first()
    return render_template('public/seo_world.html', website_settings=website_settings, keywordone=keywordone, keywordtwo=keywordtwo, location=location)
