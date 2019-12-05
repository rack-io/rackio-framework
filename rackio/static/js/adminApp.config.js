'use strict';

var schedulizer = angular.module('adminApp').
  config(['$routeProvider',
    function config($routeProvider) {
      $routeProvider.
      when('/', {
        template: '<home></home>'
      }).
      otherwise('/');
  }
]);