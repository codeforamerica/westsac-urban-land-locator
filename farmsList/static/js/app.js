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
      };
  $scope.highlightParcel = function(farmId) {
    zoomPanTo(farmId);
  };
  $scope.highlightParcelOnMap = function(farmId) {
    var map = mapboxService.getMapInstances()[0],
        farm = getFarm(farmId);
    console.log(farm);
    map.eachLayer(function (layer) {
      if (layer.getLatLng !== undefined) {
        var latLng = layer.getLatLng();
        if (latLng.lat == farm.center.lat && latLng.lng == farm.center.lng) {
          layer.setOpacity(1);
        } else {
          layer.setOpacity(.5);
        }
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
        "lng": -121.51247978210449
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
        "lng": -121.53467978210449,
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
  var previouslySelectedLayer,
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
            layer.on('click', function() {
              var applyParcelDefualts = function(parcel) {
                parcel.email = parcel.email || 'aaronl@cityofwestsacramento.org';
                parcel.zoning = parcel.zoning || 'Unspecified';
                parcel.developmentPlan = parcel.developmentPlan || 5;
                parcel.restrictions = parcel.restrictions || 'None';
              };
              // This is a dumb api failure, but this is the way to change the style of a feature layer...
              leafletData.getMap('known-parcels-map').then(function(map) {
                if (previouslySelectedLayer) {
                  map.removeLayer(previouslySelectedLayer);
                  previouslySelectedLayer.setStyle(unselectedParcelStyle);
                  map.addLayer(previouslySelectedLayer);
                }
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
                previouslySelectedLayer = layer;
              });
              // End dumb api failure compensation code
              $scope.parcel = feature.properties.parcel;
              applyParcelDefualts($scope.parcel);
              var geoJSON = feature.geometry;
              document.getElementById('newParcelGeometry').value = JSON.stringify(geoJSON);
              document.getElementById('newParcelSize').value = (turf.area(geoJSON) / 4046.85642).toFixed(2);
              document.getElementById('newParcelCenter').value = JSON.stringify(turf.centroid(geoJSON));
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
/*
  var tileLayer = {
    name: 'Countries',
    type: 'xyz',
    url: 'http://{s}.tiles.mapbox.com/v3/milkator.press_freedom/{z}/{x}/{y}.png',
    visible: true,
    layerOptions: {
      attribution: 'Mapbox and OpenStreetMap',
      showOnSelector: false
    }
  };

  var utfGrid = {
    name: 'UtfGrid',
    type: 'utfGrid',
    url: 'http://{s}.tiles.mapbox.com/v3/milkator.press_freedom/{z}/{x}/{y}.grid.json?callback={cb}',
    visible: true,
    pluginOptions: {
      maxZoom: 5,
      resolution: 4
    }
  };

  var group = {
    name: 'Group Layer',
    type: 'group',
    visible: true,
    layerOptions: {
      layers: [ tileLayer, utfGrid],
      maxZoom: 5
    }
  };

  $scope.layers['overlays']['Group Layer'] = group;

  $scope.$on('leafletDirectiveMap.utfgridMouseover', function(event, leafletEvent) {
    $scope.country = leafletEvent.data.name;
  });

  $scope.$on('leafletDirectiveMap.utfgridClick', function(event, leafletEvent) {
    console.log(leafletEvent.data.name);
    if(leafletEvent.data.name === 'Ecuador') {
      alert('You clicked on Ecuador. Congratulations; you win!');
    }
  });
  */
}]);
