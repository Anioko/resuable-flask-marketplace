from flask import Blueprint, flash, redirect, render_template, request, make_response, session
# from flask_jwt_extended import create_access_token
from flask_login import current_user, login_required, login_user, logout_user

from app.decorators import anonymous_required
from app.email import send_email
from app.blueprints.main.forms import *
from app.models import *
from app.models import Photo
import datetime

from .apis import GetMessages, PostMessage, ToggleFollow
from .forms import *
from app.blueprints.api import main_api

account = Blueprint('account', __name__)




@account.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    next = ''
    if 'next' in request.values:
        next = request.values['next']
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user_instance = User.query.filter_by(email=form.email.data).first()
            if user_instance is not None and user_instance.password_hash is not None and \
                    user_instance.verify_password(form.password.data):
                login_user(user_instance, form.remember_me.data)
                user_cart = MCart.query.filter_by(user_id=current_user.id).order_by(MCart.id.desc()).first()
                if user_cart:
                    MCart.query.filter_by(user_id=current_user.id).filter(MCart.id != user_cart.id).delete()
                else:
                    session_id = session['cart_id']
                    cart = MCart.query.filter_by(session_id=session_id).order_by(MCart.id.desc()).first()
                    if cart:
                        MCart.query.filter_by(session_id=session_id).filter(MCart.id != cart.id).delete()
                        cart.user_id = current_user.id
                        db.session.add(cart)
                        db.session.commit()
                if request.form['next'] != '':
                    resp = make_response(redirect(request.form['next']))
                    resp.set_cookie('buyer_jwt', 'bar', max_age=0)
                    resp.set_cookie('jwt_token', create_access_token(identity=form.email.data), expires=datetime.datetime.now() + datetime.timedelta(days=30))
                    return resp
                flash('You are now logged in. Welcome back!', 'success')
                resp = make_response(redirect(url_for('main.index')))
                resp.set_cookie('buyer_jwt', 'bar', max_age=0)
                resp.set_cookie('jwt_token', create_access_token(identity=user_instance.id),
                                expires=datetime.datetime.now() + datetime.timedelta(days=30))
                return resp
            else:
                flash('Invalid email or password.', 'form-error')
    return render_template('account/login.html', form=form, next=next)


@account.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    """Register a new user, and send them a confirmation email."""
    form = RegistrationForm()
    choices = [('0', "No Recruiter")]+[('{}'.format(user.id), user.full_name) for user in User.query.filter_by(profession='Recruiter').all()]
    form.recruiter.choices = choices
    form.recruiter.process_data(form.recruiter.data)
    # print(form.recruiter.data, form.recruiter.choices, form.profession.data)
    if request.method == 'GET':
        return render_template('account/register.html', form=form)
    else:
        if form.validate_on_submit():
            profession = form.profession.data if form.profession.data != 'OTHER SPECIFY' else form.custom_profession.data
            recruiter_id = None if form.profession.data == 'Recruiter' or form.recruiter.data == '0' else form.recruiter.data
            # print(recruiter_id)
            user_instance = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                gender=form.gender.data,
                profession=profession,
                recruiter_id=recruiter_id,
                area_code=form.area_code.data,
                mobile_phone=form.mobile_phone.data,
                #summary_text=form.summary_text.data,
                zip=form.zip.data,
                city=form.city.data,
                state=form.state.data,
                country=form.country.data,
                password=form.password.data)
            db.session.add(user_instance)
            db.session.commit()
            db.session.refresh(user_instance)
            MOrder.query.filter_by(email=user_instance.email).update({'buyer_id': user_instance.id}, synchronize_session='evaluate')
            if request.files['photo']:
                image_filename = images.save(request.files['photo'])
                image_url = images.url(image_filename)
                picture_photo = Photo(
                    image_filename=image_filename,
                    image_url=image_url,
                    user_id=user_instance.id,
                )
                db.session.add(picture_photo)
            db.session.commit()
            token = user_instance.generate_confirmation_token()
            confirm_link = url_for('account.confirm', token=token, _external=True)
            get_queue().enqueue(
                send_email,
                recipient=user_instance.email,
                subject='Confirm Your Account',
                template='account/email/confirm',
                user=user_instance.id,
                confirm_link=confirm_link)
            flash('A confirmation link has been sent to {}.'.format(user_instance.email), 'warning')
            if current_user.is_anonymous:
                return redirect(url_for('account.login'))
        else:
            flash('Error! Data was not added.', 'error')
        return render_template('account/register.html', form=form)


@account.route('/logout')
@login_required
def logout():
    user_cart = MCart.query.filter_by(user_id=current_user.id).order_by(MCart.id.desc()).first()
    if user_cart:
        MCart.query.filter_by(user_id=current_user.id).filter(MCart.id != user_cart.id).delete()
        user_cart.session_id = 'NONE'
        db.session.add(user_cart)
        db.session.commit()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public.index'))


@account.route('/manage/info', methods=['GET'])
@login_required
def manage():
    return render_template('account/manage.html', user=current_user, form=None)


@account.route('/manage/profile', methods=['GET'], defaults={'active': 'posts', 'page': 1})
@account.route('/manage/profile/<active>', methods=['GET'], defaults={'page': 1})
@account.route('/manage/profile/<active>/page/<int:page>', methods=['GET'])
def profile(active, page):
    return render_template('main/profile.html', user=current_user, current_user=current_user,
                           id=current_user.id, active=active)


@account.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Respond to existing user's request to reset their password."""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_password_reset_token()
            reset_link = url_for(
                'account.reset_password', token=token, _external=True)
            get_queue().enqueue(
                send_email,
                recipient=user.email,
                subject='Reset Your Password',
                template='account/email/reset_password',
                user=user.id,
                reset_link=reset_link)
        flash('A password reset link has been sent to {}.'.format(
            form.email.data), 'warning')
        return redirect(url_for('account.login'))
    return render_template('account/reset_password.html', form=form)


@account.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset an existing user's password."""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email address.', 'form-error')
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('account.login'))
        else:
            flash('The password reset link is invalid or has expired.',
                  'form-error')
            return redirect(url_for('main.index'))
    return render_template('account/reset_password.html', form=form)


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('main.index'))
        else:
            flash('Original password is invalid.', 'form-error')
    return render_template('account/manage.html', form=form)


@account.route('/manage/update-profile', methods=['GET', 'POST'])
@login_required
def change_profile_details():
    """Respond to existing user's request to change their profile details."""
    user_instance = current_user
    form = ChangeProfileForm(obj=user_instance)
    choices = [('0', "No Recruiter")]+[('{}'.format(user.id), user.full_name) for user in User.query.filter_by(profession='Recruiter').all()]
    form.recruiter.choices = choices
    form.recruiter.process_data(form.recruiter.data)
    if request.method == 'GET' and (user_instance.profession, user_instance.profession) not in form.profession.choices:
        form.profession.default = 'OTHER SPECIFY'
        form.profession.process_data(form.profession.default)
        form.custom_profession.process_data(user_instance.profession)

    if request.method == 'GET':
        form.recruiter.process_data(user_instance.recruiter_id)

    if request.method == 'POST':
        if form.validate_on_submit():
            profession = form.profession.data if form.profession.data != 'OTHER SPECIFY' else form.custom_profession.data
            recruiter_id = None if form.profession.data == 'Recruiter' or form.recruiter.data == '0' else form.recruiter.data
            del form.recruiter
            form.populate_obj(user_instance)
            user_instance.profession = profession
            user_instance.recruiter_id = recruiter_id
            db.session.add(user_instance)
            if request.files['photo']:
                image_filename = images.save(request.files['photo'])
                image_url = images.url(image_filename)
                picture_photo = Photo.query.filter_by(user_id=current_user.id).first()
                if not picture_photo:
                    picture_photo = Photo(
                        image_filename=image_filename,
                        image_url=image_url,
                        user_id=current_user.id,
                    )
                else:
                    picture_photo.image_filename = image_filename
                    picture_photo.image_url = image_url
                db.session.add(picture_photo)
            db.session.commit()
            flash('You have successfully updated your profile',
                  'success')
            return redirect(url_for('account.change_profile_details'))
        else:
            flash('Unsuccessful.', 'warning')
    return render_template('account/manage.html', form=form)


@account.route('/manage/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Respond to existing user's request to change their email."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            change_email_link = url_for(
                'account.change_email', token=token, _external=True)
            get_queue().enqueue(
                send_email,
                recipient=new_email,
                subject='Confirm Your New Email',
                template='account/email/change_email',
                # current_user is a LocalProxy, we want the underlying user
                # object
                user=current_user.id,
                change_email_link=change_email_link)
            flash('A confirmation link has been sent to {}.'.format(new_email),
                  'warning')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/manage.html', form=form)


@account.route('/manage/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    """Change existing user's email with provided token."""
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.route('/confirm-account')
@login_required
def confirm_request():
    """Respond to new user's request to confirm their account."""
    token = current_user.generate_confirmation_token()
    confirm_link = url_for('account.confirm', token=token, _external=True)
    get_queue().enqueue(
        send_email,
        recipient=current_user.email,
        subject='Confirm Your Account',
        template='account/email/confirm',
        # current_user is a LocalProxy, we want the underlying user object
        user=current_user.id,
        confirm_link=confirm_link)
    flash('A new confirmation link has been sent to {}.'.format(
        current_user.email), 'warning')
    return redirect(url_for('main.index'))


@account.route('/confirm-account/<token>')
@login_required
def confirm(token):
    """Confirm new user's account with provided token."""
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm_account(token):
        flash('Your account has been confirmed.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.route(
    '/join-from-invite/<int:user_id>/<token>', methods=['GET', 'POST'])
def join_from_invite(user_id, token):
    """
    Confirm new user's account with provided token and prompt them to set
    a password.
    """
    if current_user is not None and current_user.is_authenticated:
        flash('You are already logged in.', 'error')
        return redirect(url_for('main.index'))

    new_user = User.query.get(user_id)
    if new_user is None:
        return redirect(404)

    if new_user.password_hash is not None:
        flash('You have already joined.', 'error')
        return redirect(url_for('main.index'))

    if new_user.confirm_account(token):
        form = CreatePasswordForm()
        if form.validate_on_submit():
            new_user.password = form.password.data
            db.session.add(new_user)
            db.session.commit()
            flash('Your password has been set. After you log in, you can '
                  'go to the "Your Account" page to review your account '
                  'information and settings.', 'success')
            return redirect(url_for('account.login'))
        return render_template('account/join_invite.html', form=form)
    else:
        flash('The confirmation link is invalid or has expired. Another '
              'invite email with a new link has been sent to you.', 'error')
        token = new_user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user_id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=new_user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=new_user.id,
            invite_link=invite_link)
    return redirect(url_for('main.index'))


@account.before_app_request
def before_request():
    """Force user to confirm email before accessing login-required routes."""
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:8] != 'account.' \
            and request.endpoint != 'static':
        return redirect(url_for('account.unconfirmed'))


@account.route('/unconfirmed')
def unconfirmed():
    """Catch users with unconfirmed emails."""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('account/unconfirmed.html')


# apis
main_api.add_resource(GetMessages, '/messages/<int:user_id>/<int:page_id>')
main_api.add_resource(PostMessage, '/messages/<int:recipient_id>')
main_api.add_resource(ToggleFollow, '/toggle_follow')
