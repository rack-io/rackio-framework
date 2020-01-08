'use strict';

// Register `tags` component, along with its associated controller and template
angular.
  module('tags').
  component('tags', {
    templateUrl: '/template/tags',
    controller: function TagsController() {
      this.test = 1;
    }
  });