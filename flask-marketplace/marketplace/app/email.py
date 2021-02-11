import os

from flask import render_template
from flask_mail import Message
from flask_mail import Mail
from sendgrid import From

from app import create_app

# from app import mail
from app.models import User, Message as UserMessage, Notification

mail = Mail()

env_file = os.path.dirname(os.path.realpath(__file__))+'/../config.env'
if os.path.exists(env_file):
    for line in open(env_file):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1].replace("\"", "")


def send_email(recipient, subject, template, **kwargs):
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME') or 'www.mediville.com'
    app.config['PREFERRED_URL_SCHEME'] = os.environ.get('PREFERRED_URL_SCHEME') or 'http'
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER') or 'smtp.sendgrid.net'
    app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT') or 587
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') or True
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL') or False
    app.config['SSL_DISABLE'] = os.environ.get('SSL_DISABLE') or False
    app.config['MAIL_AUTH_TYPE'] = os.environ.get('MAIL_AUTH_TYPE') or 'sendgrid'
    app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY') or None
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    app.config['MAIL_DEFAULT_SENDER_NAME'] = os.environ.get('MAIL_DEFAULT_SENDER_NAME') or 'Mediville Team'
    app.config['EMAIL_SENDER'] = app.config['MAIL_DEFAULT_SENDER']
    app.config['MAIL_SUPPRESS_SEND'] = False
    mail.init_app(app)
    with app.app_context():
        if app.config['MAIL_AUTH_TYPE'] == 'sendgrid':
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail as SendGridMail
            data = kwargs
            for key in kwargs.keys():
                if key == 'user':
                    data[key] = User.query.get(kwargs[key])
                if key == 'related':
                    data[key] = User.query.get(kwargs[key])
                elif key == 'message':
                    data[key] = UserMessage.query.get(kwargs[key])
                elif key == 'notification':
                    data[key] = Notification.query.get(kwargs[key])
            message = SendGridMail(
                from_email=From(email=app.config['MAIL_DEFAULT_SENDER'], name=app.config['MAIL_DEFAULT_SENDER_NAME']),
                to_emails=recipient,
                subject=app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
                html_content=render_template(template + '.html', current_user=data['user'], **data))
            try:
                sg = SendGridAPIClient(app.config['SENDGRID_API_KEY'])
                response = sg.send(message)
                # print(response.status_code)
                # print(response.body)
                # print(response.headers)
            except Exception as e:
                # print(e)
                # print(message.get())
                pass
                # print(e.message)
        else:
            msg = Message(
                app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
                sender=(app.config['MAIL_DEFAULT_SENDER_NAME'], app.config['EMAIL_SENDER']),
                recipients=[recipient])
            msg.body = render_template(template + '.txt', **kwargs)
            msg.html = render_template(template + '.html', **kwargs)
            mail.send(msg)
