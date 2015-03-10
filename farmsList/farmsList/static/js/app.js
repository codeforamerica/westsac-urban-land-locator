angular.module('listApp', [])
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
  })
.controller('MainController', function($scope){
  $scope.list = ['Grant', 'Natasha', 'Imanol'];
});
