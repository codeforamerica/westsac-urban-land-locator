# -*- coding: utf-8 -*-
'''Public section, including homepage and signup.'''
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session)
from flask_mail import Message
from flask.ext.login import login_user, login_required, logout_user

from farmsList.extensions import mail, login_manager
from farmsList.user.models import User
from farmsList.public.forms import LoginForm, ContactLandOwnerForm
from farmsList.public.models import Farmland
from farmsList.user.forms import RegisterForm
from farmsList.utils import flash_errors
from farmsList.database import db

blueprint = Blueprint('public', __name__, static_folder="../static")

@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))

@blueprint.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)

@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))

@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        new_user = User.create(username=form.username.data,
                        email=form.email.data,
                        password=form.password.data,
                        active=True)
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)

@blueprint.route("/contact-land-owner/<int:farmlandId>", methods=["GET", "POST"])
def contactLandOwner(farmlandId):
    form = ContactLandOwnerForm(request.form)
    if form.validate_on_submit():
        farmland = Farmland.query.filter_by(id=farmlandId).all()[0]
        address = '' if farmland.address is None else farmland.address
        msg = Message("Hello", recipients=[form.email.data])
        msg.body = "Message body"
        msg.html = "<html><body><b>HTML</b> message <i>body</i><p>Thanks for requesting information about the property at" + \
                address + \
                "</p></body></html>"
        mail.send(msg)
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template("public/contact-land-owner.html", form=form)

@blueprint.route("/farmland-details/<int:farmlandId>")
def farmlandDetails(farmlandId):
    return render_template("public/farmland-details.html")

@blueprint.route("/about/")
def about():
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)
