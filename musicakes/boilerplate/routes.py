from flask import render_template

from . import bp

from ..session_utils import (
    get_user_data
)

@bp.route('/about', methods=['GET'])
def show_about_us():

    data = get_user_data()

    return render_template('boilerplate/about.html', userinfo=data)


@bp.route('/faq', methods=['GET'])
def show_faq():

    data = get_user_data()

    return render_template('boilerplate/faq.html', userinfo=data)

@bp.route('/terms', methods=['GET'])
def show_terms_of_use():

    data = get_user_data()

    return render_template('boilerplate/terms.html', userinfo=data)

@bp.route('/privacy', methods=['GET'])
def show_privacy_policy():

    data = get_user_data()

    return render_template('boilerplate/privacy.html', userinfo=data)
