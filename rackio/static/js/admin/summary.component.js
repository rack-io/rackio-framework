'use strict';

// Register `summary` component, along with its associated controller and template
angular.
  module('summary').
  component('summary', {
    templateUrl: '/template/summary',
    controller: function SummaryController() {
      this.test = 1;
    }
  });