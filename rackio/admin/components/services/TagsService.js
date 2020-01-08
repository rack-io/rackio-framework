(function(){
  'use strict';

  angular.module('app')
    .service('tagsService', [
    '$http',
    tagsService
  ]);

  function tagsService($http){

    return {
      getTags: $http.get('/api/tags', { cache: true })
    };
  }
})();
