from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user

from app import db
from app.blueprints.account.forms import ContactForm
from app.models import EditableHTML, ContactMessage, LandingSetting, OurBrand, User, MCategory, MProduct, MSettings
from app.blueprints.public.forms import PublicContactForm

public = Blueprint('public', __name__)

@public.route('/public')
def index():
    return redirect(url_for('main.index'))


@public.route('/about')
def about():
    website_settings = MSettings.query.first()
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('public/about.html', website_settings=website_settings, editable_html_obj=editable_html_obj)


@public.route('/contact', methods=['GET', 'POST'])
def contact():
    website_settings = MSettings.query.first()
    if current_user.is_authenticated:
        form = ContactForm()
    else:
        form = PublicContactForm()
    editable_html_obj = EditableHTML.get_editable_html('contact')
    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.is_authenticated:
                contact_message = ContactMessage(
                    user_id=current_user.id,
                    text=form.text.data
                )
            else:
                contact_message = ContactMessage(
                    name=form.name.data,
                    email=form.email.data,
                    text=form.text.data
                )
            db.session.add(contact_message)
            db.session.commit()
            flash('Successfully sent contact message.', 'success')
            return redirect(url_for('public.contact'))
    return render_template('public/contact.html', website_settings=website_settings, editable_html_obj=editable_html_obj, form=form)


@public.route('/privacy')
def privacy():
    website_settings = MSettings.query.first()
    editable_html_obj = EditableHTML.get_editable_html('privacy')
    return render_template('public/privacy.html', website_settings=website_settings, editable_html_obj=editable_html_obj)


@public.route('/terms')
def terms():
    website_settings = MSettings.query.first()
    editable_html_obj = EditableHTML.get_editable_html('terms')
    return render_template('public/terms.html', website_settings=website_settings, editable_html_obj=editable_html_obj)


@public.route('/faq')
def faq():
    website_settings = MSettings.query.first()
    editable_html_obj = EditableHTML.get_editable_html('faq')
    return render_template('public/faq.html', website_settings=website_settings, editable_html_obj=editable_html_obj)

@public.route('/payment')
def payment():
    website_settings = MSettings.query.first()
    editable_html_obj = EditableHTML.get_editable_html('payment')
    return render_template('public/payment.html', website_settings=website_settings, editable_html_obj=editable_html_obj)

@public.route('/delivery')
def delivery():
    website_settings = MSettings.query.first()
    editable_html_obj = EditableHTML.get_editable_html('delivery')
    return render_template('public/delivery.html', website_settings=website_settings, editable_html_obj=editable_html_obj)
