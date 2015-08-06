import json
import jsonpickle
from decimal import Decimal

from flask import Blueprint
from farmsList.public.models import Parcel, Farmland, AdditionalLayer

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
	farmlandData = Farmland.query.filter(Farmland.public == True).all()
	for farmland in farmlandData:
		farmland.center = json.loads(str(farmland.center))
		farmland = pre_json_encode(farmland)
	return jsonpickle.encode(farmlandData, unpicklable=False, make_refs=False)

@blueprint.route("/farmland/<int:farmlandId>", methods=["GET", "POST"])
def api_farmland_by_id(farmlandId):
	farmlandData = Farmland.query.filter_by(id=farmlandId).all()[0]
	farmlandData.center = json.loads(str(farmlandData.center))
	farmlandData = pre_json_encode(farmlandData)
	return jsonpickle.encode(farmlandData, unpicklable=False, make_refs=False)

@blueprint.route("/tax-incentive-zones", methods=["GET", "POST"])
def tax_incentive_zones():
	taxIncentiveZones = AdditionalLayer.query.filter_by(name="taxIncentive").all()
	if len(taxIncentiveZones) > 0:
		taxIncentiveZones = taxIncentiveZones[0]
	return jsonpickle.encode(taxIncentiveZones, unpicklable=False, make_refs=False)
