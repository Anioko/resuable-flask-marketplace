import operator

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from flask_sqlalchemy import Pagination
from sqlalchemy import desc, func
from app.email import send_email
from .forms import *
from ...utils import Struct

main = Blueprint('main', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/home')
@login_required
def index():
    check_org_exist = db.session.query(Organisation).filter_by(user_id=current_user.id).first()
    return render_template('main/user_dashboard.html', check_org_exist=check_org_exist)

@main.route('/search')
def search():
    query = request.args.get('query')
    page = request.args.get('page')
    search_type = request.args.get('type')
    sort_by = request.args.get('sort_by')
    sort_dir = request.args.get('sort_dir')

    query = query if query is not None else ''
    page = page if page is not None else 1
    try:
        page = int(page)
    except:
        page = 1
    search_type = search_type if search_type is not None else ''
    sort_by = sort_by if sort_by is not None else ''
    sort_dir = sort_dir if sort_dir is not None else ''
    if len(query) < 3:
        flash("Search Query must be at least 3 characters", "error")
        return render_template("main/search_results.html", query=query, search_type=search_type, sort_by=sort_by,
                               sort_dir=sort_dir, results=[])
    results = []
    if search_type == '':
##        job_results = Job.query.whooshee_search(query, order_by_relevance=0).all()
##        user_results = User.query.whooshee_search(query, order_by_relevance=0).all()
##        questions_results = Question.query.whooshee_search(query, order_by_relevance=0).all()
        products_results = MProduct.query.whooshee_search(query, order_by_relevance=0).all()

##        job_results_count = Job.query.whooshee_search(query, order_by_relevance=0).count()
##        user_results_count = User.query.whooshee_search(query, order_by_relevance=0).count()
##        questions_results_count = Question.query.whooshee_search(query, order_by_relevance=0).count()
        products_results_count = MProduct.query.whooshee_search(query, order_by_relevance=0).count()

##        all_results = job_results + user_results + questions_results + products_results
##        all_count = job_results_count + user_results_count + questions_results_count + products_results_count
        all_results = products_results
        all_count = products_results_count
        results = sorted(all_results, key=operator.attrgetter("score"))
        results.reverse()
        results = results[(page-1)*40:page*40]
        paginator = Pagination(items=results, page=page, per_page=40, query=None, total=all_count)
        results = paginator

##    elif search_type == 'people':
##        results = User.query.whooshee_search(query, order_by_relevance=-1).paginate(page, per_page=40)
##        # results = sorted(user_results, key=operator.attrgetter("score"))
##    elif search_type == 'jobs':
##        results = Job.query.whooshee_search(query, order_by_relevance=-1).paginate(page, per_page=40)
##        # results = sorted(job_results, key=operator.attrgetter("score"))
##    elif search_type == 'questions':
##        results = Question.query.whooshee_search(query, order_by_relevance=-1).paginate(page, per_page=40)
##        # results = sorted(questions_results, key=operator.attrgetter("score"))
    elif search_type == 'products':
        results = MProduct.query.whooshee_search(query, order_by_relevance=10).paginate(page, per_page=10)
        # results = sorted(products_results, key=operator.attrgetter("score"))

    return render_template("main/search_results.html", query=query, search_type=search_type, sort_by=sort_by,
                           sort_dir=sort_dir, results=results)

@main.route('/feed')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('public.index'))
    ''' this is where users will see their feeds'''
    return render_template('main/user_feed.html')


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    return redirect(url_for('account.profile'))


@main.route('/list/', defaults={'page': 1})
@main.route('/list/page/<int:page>', methods=['GET'])
@login_required
def select_section(page):
    paginated = User.query.filter(User.id != current_user.id).order_by(User.id.desc()).paginate(page, per_page=25)
    return render_template('main/selection.html', paginated=paginated)


@main.route('/profile/<int:user_id>/', methods=['GET'], defaults={'active': 'posts', 'page': 1})
@main.route('/profile/<int:user_id>/<active>', methods=['GET'], defaults={'page': 1})
@main.route('/profile/<int:user_id>/<active>/page/<page>', methods=['GET'])
def user_detail(user_id, active, page):
    """Provide HTML page with all details on a given user """
    user = User.query.get_or_404(user_id)
    if active == 'posts':
        items = user.posts.paginate(page, per_page=10)
    elif active == 'questions':
        items = user.questions.paginate(page, per_page=10)
    else:
        items = []
    user_id = Photo.user_id
    photo = Photo.query.filter_by(id=user_id).limit(1).all()
    return render_template('public/profile.html', user=user, current_user=current_user, photo=photo, id=User.id,
                           items=items)


@main.route('/user/<int:id>/<full_name>', defaults={'active': 'posts', 'page': 1})
@main.route('/user/<int:id>/<full_name>/<active>', defaults={'page': 1})
@main.route('/user/<int:id>/<full_name>/<active>/page/<int:page>')
@login_required
def user(id, full_name, active, page):
    user = db.session.query(User).filter(User.id == id, User.full_name == full_name).first()
    edit_form = PostForm()
    if user == current_user:
        return redirect(url_for('main.profile', active=active))
    return render_template('main/profile.html', user=user, edit_form=edit_form)  # , photo=photo)


@main.route('/photo/upload', methods=['GET', 'POST'])
@login_required
def photo_upload():
    ''' check if photo already exist, if it does, send to homepage. Avoid duplicate upload here'''
    check_photo_exist = db.session.query(Photo).filter(Photo.user_id == current_user.id).count()
    if check_photo_exist >= 1:
        pass
        # return redirect(url_for('main.index'))
    form = PhotoForm()
    if request.method == 'POST':
        if form.validate_on_submit():
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
            flash("Image saved.")
            return redirect(url_for('main.index'))
        else:
            flash('ERROR! Photo was not saved.', 'error')
    return render_template('main/upload.html', form=form)


@main.route('/invite-colleague', methods=['GET', 'POST'])
@login_required
def invite_user():
    """Invites a new user to create an account and set their own password."""

    form = InviteUserForm()
    if form.validate_on_submit():
        invited_by = db.session.query(User).filter_by(id=current_user.id).first()
        user = User(
            invited_by=invited_by.full_name,
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
            invite_by=invited_by
        )
        flash('User {} successfully invited'.format(user.full_name),
              'form-success')
        return redirect(url_for('main.index'))
    return render_template('main/new_user.html', form=form)


@main.route('/conversation/<recipient>/<full_name>', methods=['GET', 'POST'])
@login_required
def send_message(recipient, full_name):
    user = User.query.filter(User.id != current_user.id).filter_by(id=recipient).first_or_404()
    for message in current_user.history(user.id):
        if message.recipient_id == current_user.id:
            message.read_at = db.func.now()
        db.session.add(message)
    db.session.commit()
    form = MessageForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            msg = Message(user_id=current_user.id, recipient=user,
                          body=form.message.data)
            db.session.add(msg)
            db.session.commit()
            user.add_notification('unread_message', {'message': msg.id, 'count': user.new_messages()},
                                  related_id=current_user.id, permanent=True)
            flash('Your message has been sent.')
            return redirect(url_for('main.send_message', recipient=user.id, full_name=user.full_name))
    return render_template('main/send_messages.html', title='Send Message',
                           form=form, recipient=user, current_user=current_user)


@main.route('/conversations', defaults={'page': 1}, methods=['GET'])
@main.route('/conversations/<page>', methods=['GET'])
@login_required
def conversations(page):
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
        page, 10, False)
    conversations = Message.query.filter(
        or_(Message.user_id == current_user.id, Message.recipient_id == current_user.id)).all()
    user_ids = [conversation.user_id for conversation in conversations] + [conversation.recipient_id for conversation in
                                                                           conversations]
    user_ids = list(set(user_ids))
    if current_user.id in user_ids:
        user_ids.remove(current_user.id)
    users = User.query.filter(User.id.in_(user_ids)).paginate(page, per_page=20)
    return render_template('main/messages.html', messages=messages.items, users=users)


@main.route('/notification/read/<notification_id>')
@login_required
def read_notification(notification_id):
    notification = current_user.notifications.filter_by(id=notification_id).first_or_404()
    notification.read = True
    db.session.add(notification)
    db.session.commit()
    if 'unread_message' in notification.name:
        user = User.query.filter_by(id=notification.related_id).first_or_404()
        link = url_for('main.send_message', recipient=user.id, full_name=user.full_name)

    return redirect(link)


@main.route('/notifications/count')
@login_required
def notifications_count():
    notifications = Notification.query.filter_by(read=False).filter_by(user_id=current_user.id).count()
    messages = current_user.new_messages()

    return jsonify({
        'status': 1,
        'notifications': notifications,
        'messages': messages
    })


@main.route('/notifications')
@login_required
def notifications():
    follow_lists = User.query.filter(User.id != current_user.id).order_by(func.random()).limit(10).all()
    users = User.query.order_by(User.full_name).all()
    notifications = current_user.notifications.all()
    parsed_notifications = []
    for notification in notifications:
        parsed_notifications.append(notification.parsed())
    parsed_notifications = sorted(parsed_notifications, key=lambda i: i['time'])
    parsed_notifications.reverse()
    parsed_notifications = parsed_notifications[0:15]
    return render_template('main/notifications.html', users=users, notifications=parsed_notifications)


@main.route('/notifications/more/<int:count>')
@login_required
def more_notifications(count):
    # follow_lists = User.query.filter(User.id != current_user.id).order_by(func.random()).limit(10).all()
    # jobs = Job.query.filter(Job.organisation != None).filter(Job.end_date >= datetime.now()).order_by(Job.pub_date.asc()).all()
    # users = User.query.order_by(User.full_name).all()
    notifications = current_user.notifications.all()
    print(len(notifications))
    parsed_notifications = []
    for notification in notifications:
        parsed_notifications.append(notification.parsed())
    parsed_notifications = sorted(parsed_notifications, key=lambda i: i['time'])
    parsed_notifications.reverse()
    if count == 0:
        parsed_notifications = parsed_notifications[0:15]
    elif count >= len(parsed_notifications):
        return "<br><br><h2>No more Notifications</h2>"
    else:
        parsed_notifications = parsed_notifications[count:count + 15]
    return render_template('main/more_notifications.html', notifications=parsed_notifications)


@main.route('/notification_test')
@login_required
def notification_test():
    n = Notification.query.get(379)
    related = User.query.get(32)
    return render_template('account/email/notification.html', user=current_user, link="http://www.google.com",
                           notification=n, related=related)
