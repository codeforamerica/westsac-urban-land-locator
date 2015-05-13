# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.login import login_required

from farmsList.public.models import Parcel
from farmsList.public.forms import NewParcel1Form
from farmsList.utils import flash_errors

blueprint = Blueprint("user", __name__, url_prefix='/users',
                        static_folder="../static")

@blueprint.route("/")
@login_required
def members():
    return render_template("users/members.html")

@blueprint.route("/new_parcel_1/", methods=['GET', 'POST'])
def new_parcel_1():
    form = NewParcel1Form(request.form)
    if form.validate_on_submit():
        new_parcel = Parcel.create(name="Test Parcel",
                        email=form.email.data,
                        address=form.address.data,
                        size=form.size.data,
                        water=form.water.data,
					    zoning=form.zoning.data,
					    developmentPlan=form.developmentPlan.data,
					    restrictions=form.restrictions.data,
					    geometry=form.geometry.data,
					    image='/static/public/images/cow-farm.png')
        flash("Thank you for adding a parcel. You can now view it in the list.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template("users/new_parcel_1.html", form=form)
