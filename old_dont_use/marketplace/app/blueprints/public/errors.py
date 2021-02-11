from flask import render_template

from app.blueprints.public.views import public


@public.app_errorhandler(403)
def forbidden(_):
    return render_template('errors/403.html'), 403


@public.app_errorhandler(404)
def page_not_found(_):
    return render_template('errors/404.html'), 404


@public.app_errorhandler(500)
def internal_server_error(_):
    return render_template('errors/500.html'), 500
