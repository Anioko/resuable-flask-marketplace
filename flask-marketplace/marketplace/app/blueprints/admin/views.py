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
from sqlalchemy import or_

from app import db
from app.blueprints.admin.forms import (
    ChangeAccountTypeForm,
    ConfirmAccountForm,
    ChangeUserEmailForm,
    ChangeUserNameForm,
    InviteUserForm,
    NewUserForm,
    BackgroundImageForm,
    SiteLogoForm,
    LandingSettingForm
)
from app.decorators import admin_required
from app.email import send_email
from app.models import MSettings, EditableHTML, Role, User, Organisation, Message, BackgroundImage, SiteLogo, LandingSetting

admin = Blueprint('admin', __name__)

from app.blueprints.admin.marketplace import *
from app.blueprints.admin.blog import *


@admin.route('/')
@login_required
@admin_required
def index():
    website_settings = MSettings.query.first()
    """Admin dashboard page."""
    return render_template('admin/index.html', website_settings=website_settings)


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    website_settings = MSettings.query.first()
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
    return render_template('admin/new_user.html', website_settings=website_settings, form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    website_settings = MSettings.query.first()
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
    return render_template('admin/new_user.html', website_settings=website_settings, form=form)


@admin.route('/users', defaults={'page': 1})
@admin.route('/users/<int:page>')
@login_required
@admin_required
def registered_users(page):
    website_settings = MSettings.query.first()
    """View all registered users."""
    users = User.query.paginate(page, per_page=50)
    users_count = User.query.count()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', website_settings=website_settings, users=users, roles=roles, users_count=users_count)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    website_settings = MSettings.query.first()
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', website_settings=website_settings, user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    website_settings = MSettings.query.first()
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
    return render_template('admin/manage_user.html', website_settings=website_settings, user=user, form=form)


@admin.route('/user/<int:user_id>/change-name', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_name(user_id):
    website_settings = MSettings.query.first()
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
    return render_template('admin/manage_user.html', website_settings=website_settings, user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    website_settings = MSettings.query.first()
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
    return render_template('admin/manage_user.html', website_settings=website_settings, user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-confirmation', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_confirmation(user_id):
    website_settings = MSettings.query.first()
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
    return render_template('admin/manage_user.html', website_settings=website_settings, user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    website_settings = MSettings.query.first()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', website_settings=website_settings, user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    website_settings = MSettings.query.first()
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
    website_settings = MSettings.query.first()
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
    website_settings = MSettings.query.first()
    editable_html_obj = EditableHTML.get_editable_html(text_type)
    return jsonify({
        'status': 1,
        'editable_html_obj': editable_html_obj.serialize
    })


@admin.route('/texts', methods=['POST', 'GET'])
@login_required
@admin_required
def texts():
    website_settings = MSettings.query.first()
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
    return render_template('admin/texts/index.html', website_settings=website_settings, editable_html_obj=editable_html_obj)


@admin.route('/orgs', defaults={'page': 1}, methods=['GET'])
@admin.route('/orgs/<int:page>', methods=['GET'])
@login_required
@admin_required
def orgs(page):
    website_settings = MSettings.query.first()
    orgs = Organisation.query.paginate(page, per_page=100)
    return render_template('admin/orgs/browse.html', website_settings=website_settings, orgs=orgs)


@admin.route('/org/<int:org_id>/_delete', methods=['POST'])
@login_required
@admin_required
def delete_org(org_id):
    website_settings = MSettings.query.first()
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
    website_settings = MSettings.query.first()
    messages_result = Message.query.paginate(page, per_page=100)
    return render_template('admin/messages/browse.html', website_settings=website_settings, messages=messages_result)


@admin.route('/message/<int:message_id>/_delete', methods=['POST'])
@login_required
@admin_required
def delete_message(message_id):
    website_settings = MSettings.query.first()
    message = Message.query.filter_by(id=message_id).first()
    db.session.delete(message)
    db.session.commit()
    flash('Successfully deleted Message.', 'success')
    return redirect(url_for('admin.messages'))


@admin.route('/contact_messages', defaults={'page': 1, 'mtype': 'primary'}, methods=['GET'])
@admin.route('/contact_messages/<string:mtype>', defaults={'page': 1}, methods=['GET'])
@admin.route('/contact_messages/<string:mtype>/<int:page>', defaults={'mtype': 'primary'}, methods=['GET'])
@login_required
@admin_required
def contact_messages(mtype, page):
    website_settings = MSettings.query.first()
    if mtype == 'primary':
        contact_messages_result = ContactMessage.query.filter_by(spam=False).order_by(
            ContactMessage.created_at.desc()).paginate(page, per_page=100)
    elif mtype == 'spam':
        contact_messages_result = ContactMessage.query.filter(
            (ContactMessage.spam == True) | (ContactMessage.spam == None)).order_by(
            ContactMessage.created_at.desc()).paginate(page, per_page=100)
        print(contact_messages_result.items)
    else:
        abort(404)
    return render_template('admin/contact_messages/browse.html', website_settings=website_settings, contact_messages=contact_messages_result, mtype=mtype)


@admin.route('/contact_message/<message_id>', methods=['GET'])
@login_required
@admin_required
def view_contact_message(message_id):
    website_settings = MSettings.query.first()
    message = ContactMessage.query.filter_by(id=message_id).first_or_404()
    message.read = True
    db.session.commit()
    return render_template('admin/contact_messages/view.html', website_settings=website_settings, contact_message=message)


@admin.route('/contact_messages/<int:message_id>/_delete', methods=['POST'])
@login_required
@admin_required
def delete_contact_message(message_id):
    website_settings = MSettings.query.first()
    message = ContactMessage.query.filter_by(id=message_id).first()
    db.session.delete(message)
    db.session.commit()
    flash('Successfully deleted Message.', 'success')
    return redirect(url_for('admin.contact_messages'))


@admin.route('/contact_messages/<int:message_id>/_toggle', methods=['POST'])
@login_required
@admin_required
def toggle_message(message_id):
    website_settings = MSettings.query.first()
    message = ContactMessage.query.filter_by(id=message_id).first()
    message.spam = not message.spam
    db.session.commit()
    flash('Successfully toggles Message status.', 'success')
    return redirect(url_for('admin.contact_messages'))


@admin.route('/contact_messages/batch_toggle', methods=['POST'])
@login_required
@admin_required
def batch_toggle():
    website_settings = MSettings.query.first()
    try:
        ids = json.loads(request.form.get('items'))
    except:
        flash('Something went wrong, pls try again.', 'error')
        return redirect(url_for('admin.contact_messages'))

    messages = ContactMessage.query.filter(ContactMessage.id.in_(ids)).all()
    print(messages)
    for message in messages:
        message.spam = not message.spam
    db.session.commit()
    flash('Successfully toggles Messages status.', 'success')
    return redirect(url_for('admin.contact_messages'))


@admin.route('/contact_messages/batch_delete', methods=['POST'])
@login_required
@admin_required
def batch_delete():
    website_settings = MSettings.query.first()
    try:
        ids = json.loads(request.form.get('items'))
    except:
        flash('Something went wrong, pls try again.', 'error')
        return redirect(url_for('admin.contact_messages'))

    messages = ContactMessage.query.filter(ContactMessage.id.in_(ids)).delete(synchronize_session=False)
    # db.session.delete(messages)
    db.session.commit()
    flash('Successfully deleted Messages.', 'success')
    return redirect(url_for('admin.contact_messages'))


@admin.route('/background/image')
@login_required
@admin_required
def added_background_image():
    """View available background image"""
    data = BackgroundImage.query.first()
    if data is None:
        return redirect(url_for('admin.add_background_image'))
    return render_template(
        'admin/background/added_image.html', data=data)

# Background Image add method
@admin.route('/background_image/add', methods=['POST', 'GET'])
@admin_required
def add_background_image():
    form = BackgroundImageForm(request.form)
    if request.method == 'POST':
        image = images.save(request.files['background_image'])
        background_image = BackgroundImage(background_image=image)
        db.session.add(background_image)
        db.session.commit()
        flash("Background Image Added Successfully .", "success")
        return redirect(url_for('admin.added_background_image'))
    return render_template('admin/background/add_image.html', form=form)

# Background Image Delete Method 
@admin.route('/background_image/delete/<int:background_image_id>', methods=['POST', 'GET'])
@admin_required
def delete_background_image(background_image_id):
    background_image_data = BackgroundImage.query.get(background_image_id)
    db.session.delete(background_image_data)
    db.session.commit()
    flash("Image Deleted Successfully.", "success")
    return redirect(url_for('admin.added_background_image'))

@admin.route('/logo')
@login_required
@admin_required
def added_logo():
    """View available logo image"""
    data = SiteLogo.query.first()
    if data is None:
        return redirect(url_for('admin.add_logo'))
    return render_template(
        'admin/logo/added_logo.html', data=data)

# Logo add method
@admin.route('/logo/add', methods=['POST', 'GET'])
@admin_required
def add_logo():
    form = SiteLogoForm(request.form)
    if request.method == 'POST':
        image = images.save(request.files['logo_image'])
        logo = SiteLogo(logo_image=image)
        db.session.add(logo)
        db.session.commit()
        flash("Logo Added Successfully .", "success")
        return redirect(url_for('admin.added_logo'))
    return render_template('admin/logo/add_logo.html', form=form)

# Logo Delete Method 
@admin.route('/logo/delete/<int:logo_id>', methods=['POST', 'GET'])
@admin_required
def delete_logo(logo_id):
    logo_data = SiteLogo.query.get(logo_id)
    db.session.delete(logo_data)
    db.session.commit()
    flash("Logo Deleted Successfully.", "success")
    return redirect(url_for('admin.add_logo'))


# Add Settings 
@admin.route('/settings/add', methods=['POST', 'GET'])
@admin_required
def add_settings():
    form = LandingSettingForm()
    if form.validate_on_submit():
        data = LandingSetting(
            title=form.title.data,
            description=form.description.data,
            twitter=form.twitter.data,
            facebook=form.facebook.data,
            instagram=form.instagram.data,
            linkedin=form.linkedin.data,
            tiktok=form.tiktok.data,
            snap_chat=form.snap_chat.data,
            youtube = form.youtube.data,
            google_analytics_id = form.google_analytics_id.data,
            other_tracking_analytics_one = form.other_tracking_analytics_one.data,
            other_tracking_analytics_two = form.other_tracking_analytics_two.data,
            other_tracking_analytics_three = form.other_tracking_analytics_three.data,
            other_tracking_analytics_four = form.other_tracking_analytics_four.data              
            )
        db.session.add(data)
        db.session.commit()
        flash("SEO Added Successfully.", "success")
        return redirect(url_for('admin.added_settings'))
    return render_template('admin/settings/add_settings.html', form=form)

@admin.route('/settings')
@login_required
@admin_required
def added_settings():
    """View all added settings."""
    data = LandingSetting.query.first()
    if data is None:
        return redirect(url_for('admin.add_settings'))
    return render_template(
        'admin/settings/added_settings.html', data=data)


# Edit Settings 
@admin.route('/settings/<int:id>/edit', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_settings(id):
    data = LandingSetting.query.filter_by(id=id).first()
    form = LandingSettingForm(obj=data)
    if form.validate_on_submit():
        data.title=form.title.data
        data.description=form.description.data
        data.twitter=form.twitter.data
        data.facebook=form.facebook.data
        data.instagram=form.instagram.data
        data.linkedin=form.linkedin.data
        data.tiktok=form.tiktok.data
        data.snap_chat=form.snap_chat.data
        data.youtube = form.youtube.data
        data.google_analytics_id = form.google_analytics_id.data
        data.other_tracking_analytics_one = form.other_tracking_analytics_one.data
        data.other_tracking_analytics_two = form.other_tracking_analytics_two.data
        data.other_tracking_analytics_three = form.other_tracking_analytics_three.data
        data.other_tracking_analytics_four = form.other_tracking_analytics_four.data 
        db.session.add(data)
        db.session.commit()
        flash("Settings Added Successfully.", "success")
        return redirect(url_for('admin.added_settings'))
    else:
        flash('ERROR! Settings was not edited.', 'error')
    return render_template('admin/settings/add_settings.html', form=form)
