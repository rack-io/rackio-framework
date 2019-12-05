'use strict';

var schedulizer = angular.module('adminApp').
  config(['$routeProvider',
    function config($routeProvider) {
      $routeProvider.
      when('/', {
        template: '<summary></summary>'
      }).
      otherwise('/');
  }
]);