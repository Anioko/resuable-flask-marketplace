from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user

seo_world = Blueprint('seo_world', __name__)



@seo_world.route('/<keywordone>-<keywordtwo>-in-<location>')
def data_location(keywordone, keywordtwo, location):
    return render_template('public/seo_world.html', keywordone=keywordone, keywordtwo=keywordtwo, location=location)
