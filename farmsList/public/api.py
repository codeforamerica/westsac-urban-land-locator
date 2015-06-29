import json
import jsonpickle
from decimal import Decimal

from flask import Blueprint
from farmsList.public.models import Parcel

blueprint = Blueprint('api', __name__, url_prefix='/api',
						static_folder="../static")

def pre_json_encode(obj):
	for key in obj.__dict__.keys():
		if isinstance(obj.__dict__[key], Decimal):
			obj.__dict__[key] = float(obj.__dict__[key])
	obj.__dict__['_sa_instance_state'] = None
	return obj

@blueprint.route("/parcel/", methods=["GET", "POST"])
def api_parcel():
	parcelData = Parcel.query.filter(Parcel.listedToPublic == True).all()
	return jsonpickle.encode(parcelData, unpicklable=False, make_refs=False)

@blueprint.route("/parcel/vacant", methods=["GET", "POST"])
def api_parcel_vacant():
	parcelData = Parcel.query.filter(Parcel.landType == 'Vacant').all()
	for parcel in parcelData:
		parcel.center = json.loads(str(parcel.center))
		parcel = pre_json_encode(parcel)
	return jsonpickle.encode(parcelData, unpicklable=False, make_refs=False)
