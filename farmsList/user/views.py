# -*- coding: utf-8 -*-
import os
from sqlalchemy import func
from farmsList.settings import ProdConfig, DevConfig

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.login import login_required
from farmsList.extensions import mail
from flask_mail import Message

from farmsList.user.models import Email
from farmsList.public.models import Farmland,Parcel
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
    farmland = Farmland.query.filter(Farmland.id == farmlandId).all()[0]
    db.session.query(Farmland).filter(Farmland.id == farmlandId).update({"public": True})
    db.session.commit()
    msg = Message("Your property is now published on Acres!", recipients=[farmland.email])
    anchorTagHtml = "<a href=\"http://" + server + "/farmland-details/" + str(farmlandId) + "\">the property listing</a>"
    msg.html = ("<html>"
                    "<body>"
                        "<p>Please, visit " + anchorTagHtml + " on Acres to see how it looks.</p>"
                        "<p>Thanks,<br>"
                            "Acres"
                        "</p>"
                    "</body>"
                "</html>")
    mail.send(msg)
    Email.create(sender=msg.sender,
                recipients=",".join(msg.recipients),
                body=msg.html)
    return redirect(url_for('public.home'))

@blueprint.route("/request-changes/<int:farmlandId>")
def reject(farmlandId):
    farmland = Farmland.query.filter(Farmland.id == farmlandId).all()[0]
    msg = Message("Your property cannot be published on Acres", recipients=[farmland.email])
    msg.html = ("<html>"
                    "<body>"
                        "<p>"
                            "We're sorry, but your property cannot be published on Acres at this time. "
                            "Someone will be reaching out to your with more information."
                        "</p>"
                        "<p>Thanks,<br>"
                            "Acres"
                        "</p>"
                    "</body>"
                "</html>")
    mail.send(msg)
    Email.create(sender=msg.sender,
                    recipients=",".join(msg.recipients),
                    body=msg.html)
    return redirect(url_for('public.home'))

@blueprint.route("/list-farmland", methods=['GET', 'POST'])
def list_farmland():
    form = NewParcel1Form(request.form)
    if form.validate_on_submit():
        address = form.address.data
        water = 0 if form.water.data == '' else form.water.data
        zoning = 'Unknown'
        soil = 'Made land'
        geometry = db.session.query(func.ST_GeomFromGeoJSON(form.geometry.data)).all()[0]
        center = db.session.query(func.ST_GeomFromGeoJSON(form.center.data)).all()[0]
        knownParcel = None
        queryResult = db.session.query(Parcel).filter(func.ST_Contains(Parcel.geom, center)).all()
        if len(queryResult) > 0:
            knownParcel = queryResult[0]
            soil = knownParcel.soil
            zoning = knownParcel.zoning
            if water == 0 and knownParcel.water > 0:
                water = knownParcel.water
        new_parcel = Farmland.create(email=form.email.data,
                        ownerName = form.ownerName.data,
                        address=address,
                        size=form.size.data,
                        hasWater = form.hasWater.data,
                        water=water,
                        developmentPlan=form.developmentPlan.data,
                        monthlyCost=form.monthlyCost.data,
                        geometry=geometry,
                        center=center,
                        zoning=zoning,
                        soil=soil,
                        public=True)
        return redirect(url_for('public.home'))
    return render_template("users/list-farmland.html", form=form)
