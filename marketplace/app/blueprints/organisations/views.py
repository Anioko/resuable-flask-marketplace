from flask import Blueprint, render_template, abort, flash, redirect, request
from flask_login import current_user, login_required

from app.decorators import admin_required
from app.email import send_email
from .forms import *

organisations = Blueprint('organisations', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@organisations.route('/home')
@login_required
def org_home():
    orgs = current_user.organisations + Organisation.query.join(OrgStaff, Organisation.id == OrgStaff.org_id). \
        filter(OrgStaff.user_id == current_user.id).all()
    return render_template('organisations/org_dashboard.html', orgs=orgs)


@organisations.route('/org/<org_id>')
@login_required
def select_org(org_id):
    org = Organisation.query.filter_by(id=org_id).first_or_404()
    print(current_user.id, org.user_id)
    if current_user.id != org.user_id and current_user not in org.get_staff():
        abort(404)
    return render_template('organisations/org_operations.html', op='home', org=org)


@organisations.route('/add/new/', methods=['GET', 'POST'])
@login_required
def create_org():
    form = OrganisationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image_filename = images.save(request.files['logo'])
            image_url = images.url(image_filename)
            org = Organisation(
                user_id=current_user.id,
                image_filename=image_filename,
                image_url=image_url,
                org_name=form.org_name.data,
                org_industry=form.org_industry.data,
                org_website=form.org_website.data,
                org_city=form.org_city.data,
                org_state=form.org_state.data,
                org_country=form.org_country.data,
                org_description=form.org_description.data
            )
            db.session.add(org)
            db.session.commit()
            flash('Data added!', 'success')
            logo = Organisation.query.filter(Organisation.logos).first()
            if logo is None:
                return redirect(url_for('organisations.logo_upload'))
            return redirect(url_for('organisations.org_home'))
        else:
            flash('Error! Data was not added.', 'error')
    return render_template('organisations/create_org.html', form=form)


@organisations.route('/<int:org_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_org(org_id):
    org = Organisation.query.filter(Organisation.user == current_user).filter_by(id=org_id).first_or_404()
    form = OrganisationForm(obj=org)
    if request.method == 'POST':
        if form.validate_on_submit():
            org.org_name = form.org_name.data,
            org.org_industry = form.org_industry.data,
            org.org_website = form.org_website.data,
            org.org_city = form.org_city.data,
            org.org_state = form.org_state.data,
            org.org_country = form.org_country.data,
            org.org_description = form.org_description.data
            if request.files['logo']:
                image_filename = images.save(request.files['logo'])
                image_url = images.url(image_filename)
                org.image_filename = image_filename
                org.image_url = image_url
            db.session.add(org)
            db.session.commit()
            flash('Data edited!', 'success')
            return redirect(url_for('organisations.org_home'))
        else:
            flash('Error! Data was not added.', 'error')
    return render_template('organisations/edit_org.html', form=form, org=org)


@organisations.route('/<org_id>/list_positions', methods=['Get', 'POST'])
@login_required
def list_positions(org_id):
    org = Organisation.query.filter_by(id=org_id).first_or_404()
    if current_user.id != org.user_id and current_user not in org.get_staff():
        abort(404)
    positions = Job.query.filter_by(organisation_id=org_id).all()
    return render_template('organisations/list_positions.html', positions=positions, org=org)


@organisations.route('/<org_id>/list_promos', methods=['Get', 'POST'])
@login_required
def list_promos(org_id):
    org = Organisation.query.filter_by(id=org_id).first_or_404()
    if current_user.id != org.user_id and current_user not in org.get_staff():
        abort(404)
    promos = Promo.query.filter_by(organisation_id=org_id).all()
    return render_template('organisations/list_promos.html', promos=promos, org=org)


@organisations.route('/<org_id>/list_staff', methods=['Get', 'POST'])
@login_required
def list_staff(org_id):
    org = Organisation.query.filter_by(id=org_id).first_or_404()
    if current_user.id != org.user_id and current_user not in org.get_staff():
        abort(404)
    staff = org.get_staff()
    return render_template('organisations/list_staff.html', staff=staff, org=org)


@organisations.route('/<org_id>/create/position', methods=['Get', 'POST'])
@login_required
def create_position(org_id):
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first_or_404()
    form = PositionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image_filename = None
            if request.files['logo']:
                image_filename = images.save(request.files['logo'])
            appt = Job(position_title=form.position_title.data,
                       creator_id=current_user.id,
                       image_filename=image_filename,
                       organisation_id=org_id,
                       position_city=form.position_city.data,
                       position_state=form.position_state.data,
                       position_country=form.position_country.data,
                       description=form.description.data,
                       end_date=form.end_date.data.strftime('%d %B, %Y'),  # ''' ##('%Y-%m-%d') Alternative '''
                       required_skill_one=form.required_skill_one.data,
                       required_skill_two=form.required_skill_two.data,
                       required_skill_three=form.required_skill_three.data,
                       required_skill_four=form.required_skill_four.data,
                       required_skill_five=form.required_skill_five.data,
                       required_skill_six=form.required_skill_six.data,
                       required_skill_seven=form.required_skill_seven.data,
                       required_skill_eight=form.required_skill_eight.data,
                       required_skill_nine=form.required_skill_nine.data,
                       required_skill_ten=form.required_skill_ten.data
                       )
            db.session.add(appt)
            db.session.commit()
            for u in appt.get_same_state_users():
                if appt.creator != u:
                    u.add_notification('new_job', {'job': appt.id}, related_id=current_user.id, permanent=True)
            flash('Vacancy added!', 'success')
            return redirect(url_for('jobs.job_details', position_id=appt.id, position_title=appt.position_title,
                                    position_city=appt.position_city, position_state=appt.position_state,
                                    position_country=appt.position_country))
        else:

            flash('ERROR! Position was not added.', 'error')
    return render_template('organisations/create_job.html', form=form, org=org)


@organisations.route('/<org_id>/create/promo', methods=['Get', 'POST'])
@login_required
def create_promo(org_id):
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first_or_404()
    form = PromoForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image_filename = None
            if request.files['logo']:
                image_filename = images.save(request.files['logo'])
            appt = Promo(promo_title=form.promo_title.data,
                       creator_id=current_user.id,
                       image_filename=image_filename,
                       organisation_id=org_id,
                       promo_city=form.promo_city.data,
                       promo_state=form.promo_state.data,
                       promo_country=form.promo_country.data,
                       description=form.description.data,
                       end_date=form.end_date.data.strftime('%d %B, %Y'),  # ''' ##('%Y-%m-%d') Alternative '''
                       requirement_one=form.requirement_one.data,
                       requirement_two=form.requirement_two.data,
                       requirement_three=form.requirement_three.data,
                       requirement_four=form.requirement_four.data,
                       requirement_five=form.requirement_five.data,
                       requirement_six=form.requirement_six.data,
                       requirement_seven=form.requirement_seven.data,
                       requirement_eight=form.requirement_eight.data,
                       requirement_nine=form.requirement_nine.data,
                       requirement_ten=form.requirement_ten.data
                       )
            db.session.add(appt)
            db.session.commit()
            flash('Vacancy added!', 'success')
            return redirect(url_for('promos.promo_details', promo_id=appt.id, promo_title=appt.promo_title,
                                    promo_city=appt.promo_city, promo_state=appt.promo_state,
                                    promo_country=appt.promo_country))
        else:

            flash('ERROR! Promo was not added.', 'error')
    return render_template('organisations/create_promo.html', form=form, org=org)


@organisations.route('/org/<org_id>/view/')
def org_view(org_id):
    """Provide HTML page with all details on an organisation profile """
    org_detail = None
    try:
        org_detail = Organisation.query.filter_by(id=org_id).first()

    except IndexError:
        pass

    if org_detail is not None:
        return render_template('organisations/org_view.html', org_detail=org_detail, org=org_detail)


    elif org_detail == None:
        return redirect(url_for('main.create_org'))

    else:
        abort(404)


@organisations.route('/<int:id>/applicants/')
@login_required
def view_applicants(id):
    position = db.session.query(Job).get(id)
    if position is None:
        abort(404)
    elif current_user.id is None:
        abort(403)
    elif position.creator_id != current_user.id:
        abort(403)
    else:
        applicants_profiles = {}
        applications = Application.query.filter(Application.position_id == id).all()
        applicants_ids = [appt.user_id for appt in applications]
        applicants = [User.query.get(user_id) for user_id in applicants_ids]
        for applicant in applicants:
            profiles = Extra.query.filter(Extra.user_id == applicant.id).first()
            if profiles:
                # encoding each id of resume
                applicants_profiles[applicant.id] = profiles
            else:
                applicants_profiles[applicant.id] = None
        # print(applicants_profiles[2])
        return render_template('organisations/applicants.html', id=id,
                               applicants=applicants, profiles=applicants_profiles)

@organisations.route('/<int:id>/submissions/')
@login_required
def view_submissions(id):
    promo = db.session.query(Promo).get(id)
    if promo is None:
        abort(404)
    elif current_user.id is None:
        abort(403)
    elif promo.creator_id != current_user.id:
        abort(403)
    else:
        participants_profiles = {}
        submissions = Submission.query.filter(Submission.promo_id == id).all()
        participant_ids = [appt.user_id for appt in submissions]
        submissions = [User.query.get(user_id) for user_id in participant_ids]
        for participant in submissions:
            profiles = Extra.query.filter(Extra.user_id == participant.id).first()
            if profiles:
                # encoding each id of resume
                participants_profiles[participant.id] = profiles
            else:
                participants_profiles[participant.id] = None
        # print(applicants_profiles[2])
        return render_template('organisations/submissions.html', id=id,
                               submissions=submissions, profiles=participants_profiles)

@organisations.route('/organisation/positions/<int:id>/applicants/send-message/', methods=['GET', 'POST'])
@login_required
@admin_required
def position_applicants_send_email(id):
    """
     View for conntacitng all aplicants of postion by e-mail.

    :param position_id: id of postion that applicants will be contacted
    :return: None
    """
    if current_user.id is None:
        abort(403)
    else:
        form = ContactForm(request.form)
        if request.method == 'POST' and form.validate():
            position = db.session.query(Job).get(id)
            if position is None:
                abort(404)
            emails = [u.email for u in position.users]
            message = Message(subject=form.subject.data,
                              sender='info@mediville.com',
                              reply_to='info@mediville.com',
                              recipients=[''],
                              bcc=emails,
                              body=form.text.data)
            mail.send(message)
            flash("Message was send.", 'success')
            return redirect(url_for('organisations.view_applicants', id=id))
        return render_template('organisations/message_send_form.html', form=form)


@organisations.route('/logo/upload', methods=['GET', 'POST'])
@login_required
def logo_upload():
    ''' check if logo already exist, if it does, send to homepage. Avoid duplicate upload here'''
    check_logo_exist = db.session.query(Logo).filter(Logo.organisation_id == Organisation.id).count()
    if check_logo_exist >= 1:
        return redirect(url_for('main.index'))
    form = LogoForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image_filename = images.save(request.files['logo'])
            image_url = images.url(image_filename)
            owner_organisation = db.session.query(Organisation).filter_by(user_id=current_user.id).first()
            logo = Logo(
                image_filename=image_filename,
                image_url=image_url,
                owner_organisation=owner_organisation.org_name,
                organisation_id=owner_organisation.id
            )
            db.session.add(logo)
            db.session.commit()
            flash("Image saved.")
            return redirect(url_for('organisations.org_home'))
        else:
            flash('ERROR! Photo was not saved.', 'error')
    return render_template('organisations/upload.html', form=form)


@organisations.route('/<org_id>/invite-staff', methods=['GET', 'POST'])
@login_required
def invite_user(org_id):
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first_or_404()
    form = InviteUserForm()
    if form.validate_on_submit():
        invited_by = db.session.query(Organisation).filter_by(user_id=current_user.id).first()
        user = User(
            invited_by=invited_by.org_name,
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
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user.id,
            invited_by=invited_by,
            invite_link=invite_link,
        )
        staff = OrgStaff(user_id=user.id, invited_by=current_user.id, org_id=org_id)
        db.session.add(staff)
        db.session.commit()
        flash('User {} successfully invited'.format(user.full_name),
              'form-success')
        return redirect(url_for('organisations.org_home'))
    return render_template('organisations/new_user.html', form=form, org=org)
