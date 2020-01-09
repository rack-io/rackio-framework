(function(){
  'use strict';

  angular.module('app')
    .service('tagsService', [
    '$http',
    tagsService
  ]);

  function tagsService($http){

    $http.defaults.cache = false;

    return {
      getTags: $http.get('/api/tags', {cache: false})
    };
  }
})();
