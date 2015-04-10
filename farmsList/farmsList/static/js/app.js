angular.module('listApp', [])
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
  })
.controller('MainController', function($scope, $http){
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
      "image": "/static/public/images/cow-farm.png"
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
      "image": "/static/public/images/cow-farm.png"
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
      "image": "/static/public/images/cow-farm.png"
    }
  ];
  $http.get('/api/parcel/').
    success(function(data, status, headers, config) {
      $scope.farms = [];
      angular.forEach(data, function(parcel) {
        parcel.size = parcel.size['py/reduce'][1]['py/tuple'][0];
        $scope.farms.push(parcel);
      });
    }).
    error(function(data, status, headers, config) {
      console.log('error getting parcel data from server');
    });
});
