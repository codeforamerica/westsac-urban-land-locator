angular.module('listApp', ['angular-mapbox','leaflet-directive'])
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
  })

.run(function(mapboxService) {
    mapboxService.init({ accessToken: 'pk.eyJ1IjoiY29kZWZvcmFtZXJpY2EiLCJhIjoiSTZlTTZTcyJ9.3aSlHLNzvsTwK-CYfZsG_Q' });
  })

.controller('MainController', function($scope, $http, mapboxService){
  var getFarm = function(farmId) {
        var _farm;
        angular.forEach($scope.farms, function(farm) {
          if (!_farm && farm.id === farmId) {
            _farm = farm;
          }
        });
        return _farm;
      },
      zoomPanTo = function(farmId) {
        var map = mapboxService.getMapInstances()[0],
            farm = getFarm(farmId);
        map.setView(L.latLng(farm.center.lat, farm.center.lng), 17, {
          pan: {
            animate: true,
            duration: .5
          },
          zoom: {
            animate: true
          }
        });
      },
      unselectedParcelStyle = {
        fillColor: "green",
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.2
      },
      selectedParcelStyle = {
        fillColor: "green",
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7
      };
  $scope.goToFarmlandDetailsPage = function(farmId) {
    document.location.href = '/farmland-details/' + farmId;
  };
  $scope.highlightParcelOnMap = function(farmId) {
    var map = mapboxService.getMapInstances()[0],
        farm = getFarm(farmId);
    map.eachLayer(function (layer) {
      if (layer.getLatLng !== undefined) {
        var latLng = layer.getLatLng();
        if (latLng.lat == farm.center.lat && latLng.lng == farm.center.lng) {
          layer.setOpacity(1);
        } else {
          layer.setOpacity(.5);
        }
      } else if (layer.feature !== undefined) {
        map.removeLayer(layer);
        if (angular.equals(layer.feature, farm.geometry)) {
          layer.setStyle(selectedParcelStyle);
        } else {
          layer.setStyle(unselectedParcelStyle);
        }
        map.addLayer(layer);
      }
    });
  };
  $scope.farms = [
    {
      "id": 1,
      "name": "Jordan Valley",
      "contact": "Diego Aranzadi",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "size": 2.1,
      "zoning": "type of zone",
      "water": "Yes - potable",
      "developmentPlans": 2,
      "center": {
        "lat": 38.58843235229309,
        "lng": -121.51357978210449
      },
      "geometry": {
        "type":"Polygon",
        "coordinates":[[[-121.51367978210449,38.58853235229309],[-121.51347978210449,38.58853235229309],[-121.51347978210449,38.58833235229309],[-121.51367978210449,38.58833235229309],[-121.51367978210449,38.58853235229309]]]
      }
    },{
      "id": 2,
      "name": "Yolo Valley",
      "contact": "Ivan Matos",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "size": 2.3,
      "zoning": "type of zone",
      "water": "Yes - potable",
      "developmentPlans": 2,
      "center": {
        "lat": 38.58843235229309,
        "lng": -121.52357978210449,
      },
      "geometry": {
        "type":"Polygon",
        "coordinates":[[[-121.52367978210449,38.58853235229309],[-121.52347978210449,38.58853235229309],[-121.52347978210449,38.58833235229309],[-121.52367978210449,38.58833235229309],[-121.52367978210449,38.58853235229309]]]
      }
    },{
      "id": 3,
      "name": "Old McDonald Farm",
      "contact": "Felix Colón",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "size": 1.8,
      "zoning": "type of zone",
      "water": "Yes - potable",
      "developmentPlans": 2,
      "center": {
        "lat": 38.58843235229309,
        "lng": -121.53357978210449,
      },
      "geometry": {
        "type":"Polygon",
        "coordinates":[[[-121.53367978210449,38.58853235229309],[-121.53347978210449,38.58853235229309],[-121.53347978210449,38.58833235229309],[-121.53367978210449,38.58833235229309],[-121.53367978210449,38.58853235229309]]]
      }
    }
  ];
  $http.get('/api/parcel/').
    success(function(data, status, headers, config) {
      if (!data || data.length === 0) {
        return;
      }
      $scope.farms = [];
      angular.forEach(data, function(parcel) {
        parcel.center = JSON.parse(parcel.center);
        parcel.center.lat = parcel.center.geometry.coordinates[1];
        parcel.center.lng = parcel.center.geometry.coordinates[0];
        // This conversion is needed because the jsonpickle
        // serialization seems forced to maintain type references
        parcel.size = parcel.size['py/reduce'][1][0]
        parcel.water = parcel.water['py/reduce'][1][0] + ' gallons per minute'
        $scope.farms.push(parcel);
      });
    }).
    error(function(data, status, headers, config) {
      console.log('error getting parcel data from server');
    });
})

.controller('PublishListingsController', ['$scope', '$http', 'leafletData', function($scope, $http, leafletData){
  $scope.parcels = [];
  var selectedLayers =[],
      unselectedParcelStyle = {
        fillColor: "green",
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.2
      };
  $http.get('/api/parcel/vacant').
    success(function(data, status, headers, config) {
      if (!data || data.length === 0) {
        return;
      }
      var features = [];
      angular.forEach(data, function(parcel) {
        parcel.center.lat = parcel.center.geometry.coordinates[1];
        parcel.center.lng = parcel.center.geometry.coordinates[0];
        features.push({
          type: "Feature",
          geometry: JSON.parse(parcel.geometry),
          properties: {
            parcel: parcel
          }
        });
      });
      data = {
        type: "FeatureCollection",
        features: features
      };
      angular.extend($scope, {
        geojson: {
          data: data,
          style: unselectedParcelStyle,
          onEachFeature: function (feature, layer) {
            var highlightSelectedParcel = function(layer) {
              leafletData.getMap('known-parcels-map').then(function(map) {
                map.removeLayer(layer);
                layer.setStyle({
                  fillColor: "green",
                  weight: 2,
                  opacity: 1,
                  color: 'white',
                  dashArray: '3',
                  fillOpacity: 0.7
                });
                map.addLayer(layer);
              });
            },
            unhighlightSelectedParcel = function(layer) {
              leafletData.getMap('known-parcels-map').then(function(map) {
                map.removeLayer(layer);
                layer.setStyle(unselectedParcelStyle);
                map.addLayer(layer);
              });
            },
            updateGeometryElements = function(geoJSON) {
              var geometryString = '',
                  area = 0,
                  centerString = '';
              if (geoJSON) {
                geometryString = JSON.stringify(geoJSON);
                area = (turf.area(geoJSON) / 4046.85642).toFixed(2);
                centerString = JSON.stringify(turf.centroid(geoJSON));
              }
              document.getElementById('newParcelGeometry').value = geometryString;
              document.getElementById('newParcelSize').value = area;
              document.getElementById('newParcelCenter').value = centerString;
            },
            updateMultiParcelSelectionGeometry = function() {
              var features = [];
              angular.forEach(selectedLayers, function(layer) {
                features.push(layer.feature);
              });
              var featureCollection = turf.featurecollection(features);
              updateGeometryElements(turf.merge(featureCollection));
            },
            addToSelectedUrbanFarmLand = function(layer) {
              highlightSelectedParcel(layer);
              selectedLayers.push(layer);
              updateMultiParcelSelectionGeometry();
            },
            removeFromSelectedUrbanFarmLand = function(layer) {
              unhighlightSelectedParcel(layer);
              selectedLayers.splice(selectedLayers.indexOf(layer), 1);
              updateMultiParcelSelectionGeometry();
            };
            layer.on('click', function(event) {
              if (event.originalEvent.shiftKey && selectedLayers.length > 0) {
                if (selectedLayers.indexOf(layer) === -1) {
                  addToSelectedUrbanFarmLand(layer);
                } else {
                  removeFromSelectedUrbanFarmLand(layer);
                }
                return;
              }
              var applyParcelDefualts = function(parcel) {
                parcel.email = parcel.email || 'aaronl@cityofwestsacramento.org';
                parcel.zoning = parcel.zoning || 'Unspecified';
                parcel.developmentPlan = parcel.developmentPlan || 5;
                parcel.restrictions = parcel.restrictions || 'None';
              };
              leafletData.getMap('known-parcels-map').then(function(map) {
                angular.forEach(selectedLayers, function(layer) {
                  unhighlightSelectedParcel(layer);
                });
                selectedLayers = [layer];
                highlightSelectedParcel(layer);  // This has to be inside the callback so order is always unhighlight, highlight.
              });
              $scope.parcel = feature.properties.parcel;
              applyParcelDefualts($scope.parcel);
              updateGeometryElements(feature.geometry);
            });
          }
        }
      });
    }).
    error(function(data, status, headers, config) {
      console.log('error getting parcel data from server in PublishListingsController');
    });

  angular.extend($scope, {
    center: {
      lat: 38.58024,
      lng: -121.5305,
      zoom: 14
    },
    layers: {
      baselayers: {
        xyz: {
          name: 'OpenStreetMap (XYZ)',
          url: 'http://{s}.tiles.mapbox.com/v4/codeforamerica.m5m971km/{z}/{x}/{y}@2x.png?access_token=pk.eyJ1IjoiY29kZWZvcmFtZXJpY2EiLCJhIjoiSTZlTTZTcyJ9.3aSlHLNzvsTwK-CYfZsG_Q',
          type: 'xyz',
          layerOptions: {
            attribution: 'Mapbox | OpenStreetMap',
            showOnSelector: false
          }
        }
      }
    }
  });
}])

.controller('FarmlandDetailsController', ['$scope', '$http', 'leafletData', '$location', function($scope, $http, leafletData, $location){
  $scope.farmland = {};
  /*
  $http.get('/api/farmland/' + $location.absUrl().split('farmland-details/')[1]).
    success(function(data, status, headers, config) {
      if (!data || data.length === 0) {
        return;
      }
      $scope.center = data.center;
      angular.extend($scope, {
        farmland: data,
        geojson: {
          data: data,
          style: {
            color: green
          }
        }
      });
    }).
    error(function(data, status, headers, config) {
      console.log('error getting farmland data from server in FarmlandDetailsController');
    });
  */
  angular.extend($scope, {
    center: {
      lat: 38.58024,
      lng: -121.5305,
      zoom: 14
    },
    layers: {
      baselayers: {
        xyz: {
          name: 'OpenStreetMap (XYZ)',
          url: 'http://{s}.tiles.mapbox.com/v4/codeforamerica.m5m971km/{z}/{x}/{y}@2x.png?access_token=pk.eyJ1IjoiY29kZWZvcmFtZXJpY2EiLCJhIjoiSTZlTTZTcyJ9.3aSlHLNzvsTwK-CYfZsG_Q',
          type: 'xyz',
          layerOptions: {
            attribution: 'Mapbox | OpenStreetMap',
            showOnSelector: false
          }
        }
      }
    }
  });
}]);
