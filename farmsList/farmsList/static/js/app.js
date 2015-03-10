angular.module('listApp', [])
.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');
  })
.controller('MainController', function($scope){
  $scope.farms = [
    {
      "title": "Jordan Valley",
      "description": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Nemo, nostrum, quis. Eos labore dignissimos provident illum quisquam tempora quasi nemo magnam at beatae consequatur debitis eum modi molestiae, temporibus accusamus! ",
      "contact": "Jordan Gregory",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "image": "http://www.moraitis.com.au/media/images/North-Queensland-Potato-Farm-e37f75d1-b49f-4a7a-954a-5daf8ac8fd56-0-2080x1544.JPG"
    },{
      "title": "Jordan Valley",
      "description": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Nemo, nostrum, quis. Eos labore dignissimos provident illum quisquam tempora quasi nemo magnam at beatae consequatur debitis eum modi molestiae, temporibus accusamus! ",
      "contact": "Jordan Gregory",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "image": "http://www.farmsunday.org/resources/000/746/284/Rowley_Farm.JPG"
    },{
      "title": "Jordan Valley",
      "description": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Nemo, nostrum, quis. Eos labore dignissimos provident illum quisquam tempora quasi nemo magnam at beatae consequatur debitis eum modi molestiae, temporibus accusamus! ",
      "contact": "Jordan Gregory",
      "phone": "530-555-1234",
      "address": "Km 41.2 West Sacramento, CA 95605",
      "image": "http://broadrundairyfarm.com/farmimages/farm%20pics%20%282%29_edited.jpg"
    }
  ];
});
