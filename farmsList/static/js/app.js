angular.module('listApp', ['angular-mapbox'])
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
  $scope.farms = [
    {
      "name": "Jordan Valley",
      "contact": "Diego Aranzadi",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "geolocation": ['longitude', 'latitutde'],
      "size": 2.1,
      "zoning": "type of zone",
      "water": "Yes - potable",
      "developmentPlans": 2,
      "center": {
        "lat": 38.58843235229309,
        "lng": -121.51247978210449
      }
    },{
      "name": "Yolo Valley",
      "contact": "Ivan Matos",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "geolocation": ['longitude', 'latitutde'],
      "size": 2.3,
      "zoning": "type of zone",
      "water": "Yes - potable",
      "developmentPlans": 2,
      "center": {
        "lat": 38.58843235229309,
        "lng": -121.52357978210449,
      }
    },{
      "name": "Old McDonald Farm",
      "contact": "Felix Colón",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "geolocation": ['longitude', 'latitutde'],
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

.controller('PublishListingsController', function($scope, $http, mapboxService){
  $scope.parcels = [];
  $http.get('/api/parcel/vacant').
    success(function(data, status, headers, config) {
      if (!data || data.length === 0) {
        return;
      }
      $scope.parcels = [];
      angular.forEach(data, function(parcel) {
        parcel.center = JSON.parse(parcel.center);
        parcel.center.lat = parcel.center.geometry.coordinates[1];
        parcel.center.lng = parcel.center.geometry.coordinates[0];
        // This conversion is needed because the jsonpickle
        // serialization seems forced to maintain type references
        parcel.size = parcel.size['py/reduce'][1][0]
        parcel.water = parcel.water['py/reduce'][1][0]
        $scope.parcels.push(parcel);
      });
    }).
    error(function(data, status, headers, config) {
      console.log('error getting parcel data from server in PublishListingsController');
    });
});
