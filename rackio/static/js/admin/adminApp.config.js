'use strict';

var schedulizer = angular.module('adminApp').
  config(['$routeProvider',
    function config($routeProvider) {
      $routeProvider.
      when('/', {
        template: '<summary></summary>'
      }).
      when('/tags', {
        template: '<tags></tags>'
      }).
      otherwise('/');
  }
]);

function getService(serviceName){
  return angular.element(document.body).injector().get(serviceName);
}