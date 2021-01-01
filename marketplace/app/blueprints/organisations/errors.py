from flask import render_template

from app.blueprints.organisations.views import organisations


@organisations.app_errorhandler(403)
def forbidden(_):
    return render_template('errors/403.html'), 403


@organisations.app_errorhandler(404)
def page_not_found(_):
    return render_template('errors/404.html'), 404


@organisations.app_errorhandler(500)
def internal_server_error(_):
    return render_template('errors/500.html'), 500
