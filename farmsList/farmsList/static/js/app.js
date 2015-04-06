angular.module('listApp', [])
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
  })
.controller('MainController', function($scope){
  $scope.farms = [
    {
      "title": "Jordan Valley",
      "contact": "Diego Aranzadi",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "geolocation": ['longitude', 'latitutde'],
      "size": 2.1,
      "zone": "type of zone",
      "water": "Yes - potable",
      "developmentPlans": 2,
      "image": "/static/public/images/cow-farm.png"
    },{
      "title": "Yolo Valley",
      "contact": "Ivan Matos",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "geolocation": ['longitude', 'latitutde'],
      "size": 2.3,
      "zone": "type of zone",
      "water": "Yes - potable",
      "developmentPlans": 2,
      "image": "/static/public/images/cow-farm.png"
    },{
      "title": "Old McDonald Farm",
      "contact": "Felix Colón",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "geolocation": ['longitude', 'latitutde'],
      "size": 1.8,
      "zone": "type of zone",
      "water": "Yes - potable",
      "developmentPlans": 2,
      "image": "/static/public/images/cow-farm.png"
    }
  ];
});
