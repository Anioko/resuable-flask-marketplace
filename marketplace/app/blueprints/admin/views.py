from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.blueprints.admin.forms import (
    ChangeAccountTypeForm,
    ConfirmAccountForm,
    ChangeUserEmailForm,
    ChangeUserNameForm,
    InviteUserForm,
    NewUserForm,
    LandingSettingForm,
    LandingImageForm,
    OurBrandForm
    
)
from app.decorators import admin_required
from app.email import send_email
from app.models import EditableHTML, Role, User, Organisation, Message, ContactMessage, LandingSetting, LandingImage, OurBrand

from flask_uploads import UploadSet, IMAGES
from flask_wtf.file import FileAllowed

admin = Blueprint('admin', __name__)
images = UploadSet('images', IMAGES)
photos = UploadSet('photos', IMAGES)
from app.blueprints.admin.marketplace import *


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')

@admin.route('/settings/dashboard/')
@login_required
@admin_required
def frontend_dashboard():
    """Frontend dashboard page."""
    return render_template('admin/frontend_settings_dashboard.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    password = form.password.data
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        invite_link = url_for('account.login', _external=True)
        invite_by = User.query.filter(User.id == current_user.id).first()
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/created_account',
            user=user.id,
            invite_link=invite_link,
            invite_by=invite_by,
            password=password
        )
        flash('User {} successfully created'.format(user.full_name),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token,
            _external=True)
        invite_by = User.query.filter(User.id == current_user.id).first()
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user.id,
            invite_link=invite_link,
            invite_by=invite_by
        )
        flash('User {} successfully invited'.format(user.full_name),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/users', defaults={'page': 1})
@admin.route('/users/<int:page>')
@login_required
@admin_required
def registered_users(page):
    """View all registered users."""
    users = User.query.paginate(page, per_page=50)
    users_count = User.query.count()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles, users_count=users_count)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'.format(
            user.full_name, user.email), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/change-name', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_name(user_id):
    """Change a user's first and last names."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserNameForm()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        db.session.add(user)
        db.session.commit()
        flash('First and last names changes successfully', 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'.format(
            user.full_name, user.role.name), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-confirmation', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_confirmation(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ConfirmAccountForm()
    if form.validate_on_submit():
        user.confirmed = form.confirmed.data
        db.session.add(user)
        db.session.commit()
        flash('User confirmed', 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name, 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/user/<int:user_id>/_seller')
@login_required
@admin_required
def toggle_user_seller(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.is_seller = not user.is_seller
    db.session.add(user)
    db.session.commit()
    flash('Successfully Changes user %s Seller Status.' % user.full_name, 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/text/<text_type>', methods=['GET'])
@login_required
@admin_required
def text(text_type):
    editable_html_obj = EditableHTML.get_editable_html(text_type)
    return jsonify({
        'status': 1,
        'editable_html_obj': editable_html_obj.serialize
    })


@admin.route('/texts', methods=['POST', 'GET'])
@login_required
@admin_required
def texts():
    editable_html_obj = EditableHTML.get_editable_html('contact')
    if request.method == 'POST':
        edit_data = request.form.get('edit_data')
        editor_name = request.form.get('editor_name')

        editor_contents = EditableHTML.query.filter_by(
            editor_name=editor_name).first()
        if editor_contents is None:
            editor_contents = EditableHTML(editor_name=editor_name)
        editor_contents.value = edit_data

        db.session.add(editor_contents)
        db.session.commit()
        flash('Successfully updated text.', 'success')
        return redirect(url_for('admin.texts'))
    return render_template('admin/texts/index.html', editable_html_obj=editable_html_obj)


@admin.route('/orgs', defaults={'page': 1}, methods=['GET'])
@admin.route('/orgs/<int:page>', methods=['GET'])
@login_required
@admin_required
def orgs(page):
    orgs = Organisation.query.paginate(page, per_page=100)
    return render_template('admin/orgs/browse.html', orgs=orgs)


@admin.route('/org/<int:org_id>/_delete', methods=['POST'])
@login_required
@admin_required
def delete_org(org_id):
    org = Organisation.query.filter_by(id=org_id).first()
    db.session.delete(org)
    db.session.commit()
    flash('Successfully deleted Organisation.', 'success')
    return redirect(url_for('admin.orgs'))


@admin.route('/messages', defaults={'page': 1}, methods=['GET'])
@admin.route('/messages/<int:page>', methods=['GET'])
@login_required
@admin_required
def messages(page):
    messages_result = Message.query.paginate(page, per_page=100)
    return render_template('admin/messages/browse.html', messages=messages_result)


@admin.route('/message/<int:message_id>/_delete', methods=['POST'])
@login_required
@admin_required
def delete_message(message_id):
    message = Message.query.filter_by(id=message_id).first()
    db.session.delete(message)
    db.session.commit()
    flash('Successfully deleted Message.', 'success')
    return redirect(url_for('admin.messages'))


@admin.route('/contact_messages', defaults={'page': 1}, methods=['GET'])
@admin.route('/contact_messages/<page>', methods=['GET'])
@login_required
@admin_required
def contact_messages(page):
    contact_messages_result = ContactMessage.query.paginate(page, per_page=100)
    return render_template('admin/contact_messages/browse.html', contact_messages=contact_messages_result)


@admin.route('/contact_message/<message_id>', methods=['GET'])
@login_required
@admin_required
def view_contact_message(message_id):
    message = ContactMessage.query.filter_by(id=message_id).first_or_404()
    return render_template('admin/contact_messages/view.html', contact_message=message)


@admin.route('/contact_messages/<int:message_id>/_delete', methods=['POST'])
@login_required
@admin_required
def delete_contact_message(message_id):
    message = ContactMessage.query.filter_by(id=message_id).first()
    db.session.delete(message)
    db.session.commit()
    flash('Successfully deleted Message.', 'success')
    return redirect(url_for('admin.contact_messages'))


@admin.route('/landing-settings', methods=['GET', 'POST'])
@admin.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def landing_setting(id=None):
    """Adds information to the landing page."""
    settings = db.session.query(LandingSetting.id).count()
    if settings == 1:
        return redirect(url_for('admin.edit_landing_setting', id=1))
    form = LandingSettingForm()
    if request.method == 'POST':
            settings = LandingSetting(
                site_name = form.site_name.data,
                title = form.title.data,
                description = form.description.data,
                
                twitter_name = form.twitter_name.data,
                facebook_name = form.facebook_name.data,
                instagram_name=form.instagram_name.data,
                linkedin_name = form.linkedin_name.data,
                tiktok_name = form.tiktok_name.data,
                snap_chat_name = form.snap_chat_name.data,
                youtube = form.youtube.data,
                blog = form.blog.data,
                about = form.about.data,
                contact = form.contact.data,
                
                faq = form.faq.data,
                
                featured_title_one = form.featured_title_one.data,
                featured_title_one_text = form.featured_title_one_text.data,
                featured_title_one_icon = form.featured_title_one_icon.data,
                featured_title_two = form.featured_title_two.data,
                featured_title_two_text = form.featured_title_two_text.data,
                featured_title_two_icon = form.featured_title_two_icon.data,
                featured_title_three = form.featured_title_three.data,
                featured_title_three_text = form.featured_title_three_text.data,
                featured_title_three_icon = form.featured_title_three_icon.data,
                
                google_analytics_id = form.google_analytics_id.data,
                other_tracking_analytics_one = form.other_tracking_analytics_one.data,
                other_tracking_analytics_two = form.other_tracking_analytics_two.data,
                block_content_one = form.block_content_one.data
            )
            db.session.add(settings)
            db.session.commit()
            flash('Settings successfully added', 'success')
            return redirect(url_for('admin.edit_landing_setting', id=id))
    return render_template('admin/new_landing_setting.html', form=form)

@admin.route('/edit-landing-settings/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_landing_setting(id):
    """Edit information to the landing page."""
    settings = LandingSetting.query.get(id)
    form = LandingSettingForm(obj=settings)
    
    if request.method == 'POST':
            form.populate_obj(settings)
            db.session.add(settings)
            db.session.commit()
            flash('Settings successfully edited', 'success')
            return redirect(url_for('admin.frontend_dashboard'))
    return render_template('admin/edit_landing_setting.html', form=form)


@admin.route('/upload', methods=['GET', 'POST'])
def upload():
    form = LandingImageForm()
    if request.method == 'POST' and 'image' in request.files:
        image = images.save(request.files['image'])
        image = LandingImage(image=image)
        db.session.add(image)
        db.session.commit()
        flash("Photo saved.")
        return redirect(url_for('admin.show', id=image.id))
    return render_template('admin/upload.html', form=form)

@admin.route('/image/<int:id>')
def show(id):
    photo = LandingImage.query.get(id)
    if photo is None:
        abort(404)
    url = images.url(photo.image)
    return render_template('admin/show.html', url=url, photo=photo)


@admin.route('/landing-brand-settings', methods=['GET', 'POST'])
@admin.route('/landing-brand-settings/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def landing_brand_setting(id=None):
    """Adds information to the landing page."""
    settings = db.session.query(OurBrand.id).count()
    if settings == 1:
        return redirect(url_for('admin.edit_landing_brand_setting', id=1))
    form = OurBrandForm()
    if request.method == 'POST':
            settings = OurBrand(

                brand_name_one = form.brand_name_one.data,
                brand_name_two = form.brand_name_two.data,
                brand_name_three = form.brand_name_three.data,
                brand_name_five = form.brand_name_five.data,
                brand_url_one = form.brand_url_five.data,
                brand_url_two = form.brand_url_five.data,
                brand_url_three = form.brand_url_five.data,
                brand_url_four = form.brand_url_five.data,
                brand_url_five = form.brand_url_five.data
            )
            db.session.add(settings)
            db.session.commit()
            flash('Settings successfully added', 'success')
            return redirect(url_for('admin.edit_landing_brand_setting', id=id))
    return render_template('admin/new_landing_brand_setting.html', form=form)


@admin.route('/edit-landing-brand-settings/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_landing_brand_setting(id):
    """Edit information to the landing page."""
    settings = OurBrand.query.get(id)
    form = OurBrandForm(obj=settings)
    
    if request.method == 'POST':
            form.populate_obj(settings)
            db.session.add(settings)
            db.session.commit()
            flash('Settings successfully edited', 'success')
            return redirect(url_for('admin.frontend_dashboard'))
    return render_template('admin/new_landing_brand_setting.html', form=form)

@admin.route('/landing-news-settings', methods=['GET', 'POST'])
@admin.route('/landing-news-settings/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def landing_news_setting(id=None):
    """Adds information to the landing page."""
    settings = db.session.query(NewsLink.id).count()
    if settings == 1:
        return redirect(url_for('admin.edit_landing_brand_setting', id=1))
    form = NewsLinkForm()
    if request.method == 'POST':
            settings = NewsLink(

                news_site_one = form.news_site_one.data,
                news_site_two = form.news_site_two.data,
                news_site_three = form.news_site_three.data,
                news_site_five = form.news_site_five.data,
                news_url_one = form.news_url_five.data,
                news_url_two = form.news_url_five.data,
                news_url_three = form.news_url_five.data,
                news_url_four = form.news_url_five.data,
                news_url_five = form.news_url_five.data
            )
            db.session.add(settings)
            db.session.commit()
            flash('Settings successfully added', 'success')
            return redirect(url_for('admin.edit_landing_brand_setting', id=id))
    return render_template('admin/new_landing_edit_setting.html', form=form)


@admin.route('/edit-landing-brand-settings/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_landing_news_setting(id):
    """Edit information to the landing page."""
    settings = NewsLink.query.get(id)
    form = NewsLinkForm(obj=settings)
    
    if request.method == 'POST':
            form.populate_obj(settings)
            db.session.add(settings)
            db.session.commit()
            flash('Settings successfully edited', 'success')
            return redirect(url_for('admin.frontend_dashboard'))
    return render_template('admin/new_landing_edit_setting.html', form=form)
