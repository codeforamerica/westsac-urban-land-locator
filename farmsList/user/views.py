# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.login import login_required
from farmsList.extensions import mail
from flask_mail import Message

from farmsList.public.models import Farmland
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
        address = form.address.data
        new_parcel = Farmland.create(email=form.email.data,
                        ownerName = form.ownerName.data,
                        address=address,
                        size=form.size.data,
                        hasWater = form.hasWater.data,
                        water=form.water.data,
                        developmentPlan=form.developmentPlan.data,
                        monthlyCost=form.monthlyCost.data,
                        geometry=form.geometry.data,
                        center=form.center.data,
                        zoning='Unknown')
        flash("Thank you for listing a property. It will appear here after it has been reviewed by the city.")
        # msg = Message("Hello", recipients=['aaronl@cityofwestsacramento.org'])
        msg = Message("Hello", recipients=['grant@codeforamerica.org'])
        msg.html = "<html><body><p>Someone tried to post property with address " + \
                address + \
                "</p></body></html>"
        mail.send(msg)
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template("users/new_parcel_1.html", form=form)
