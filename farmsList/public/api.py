import json
import jsonpickle
from decimal import Decimal

from flask import Blueprint
from farmsList.public.models import Parcel, Farmland

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
	farmlandData = Farmland.query.all()
	for farmland in farmlandData:
		farmland.center = json.loads(str(farmland.center))
		farmland = pre_json_encode(farmland)
	return jsonpickle.encode(farmlandData, unpicklable=False, make_refs=False)

@blueprint.route("/parcel/vacant", methods=["GET", "POST"])
def api_parcel_vacant():
	parcelData = Parcel.query.filter(Parcel.landType == 'Vacant').limit(100).all()  # limit 100 is for testing (force fasterness :)
	for parcel in parcelData:
		parcel.center = json.loads(str(parcel.center))
		parcel = pre_json_encode(parcel)
	return jsonpickle.encode(parcelData, unpicklable=False, make_refs=False)

@blueprint.route("/farmland/<int:farmlandId>", methods=["GET", "POST"])
def api_farmland_by_id(farmlandId):
	print "1"
	farmlandData = Farmland.query.filter_by(id=farmlandId).all()[0]
	print "2"
	farmlandData.center = json.loads(str(farmlandData.center))
	print "3"
	farmlandData = pre_json_encode(farmlandData)
	print "4"
	return jsonpickle.encode(farmlandData, unpicklable=False, make_refs=False)
