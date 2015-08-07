# -*- coding: utf-8 -*-
import os
from farmsList.settings import ProdConfig, DevConfig

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.login import login_required
from farmsList.extensions import mail
from flask_mail import Message

from farmsList.public.models import Farmland
from farmsList.public.forms import NewParcel1Form
from farmsList.utils import flash_errors
from farmsList.database import db

if os.environ.get("FARMSLIST_ENV") == 'prod':
    server = ProdConfig().HTTP_SERVER
else:
    server = DevConfig().HTTP_SERVER

blueprint = Blueprint("user", __name__, url_prefix='/users',
                        static_folder="../static")

@blueprint.route("/approve/<int:farmlandId>")
def approve(farmlandId):
    db.session.query(Farmland).filter(Farmland.id == farmlandId).update({"public": True})
    db.session.commit()
    return redirect(url_for('public.home'))

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
        # msg = Message("Review a new property on Acres", recipients=['aaronl@cityofwestsacramento.org'])
        msg = Message("Review a new property on Acres", recipients=['grantrobertsmith@gmail.com'])
        anchorTagHtml = "<a href=\"http://" + server + "/farmland-approval/" + str(new_parcel.id) + "\">review a proerty</a>"
        msg.html = ("<html>"
                        "<body>"
                            "<p>Please, " + anchorTagHtml + " to publish it on Acres.</p>"
                            "<p>Thanks,<br>"
                                "Acres"
                            "</p>"
                        "</body>"
                    "</html>")
        mail.send(msg)
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template("users/new_parcel_1.html", form=form)
