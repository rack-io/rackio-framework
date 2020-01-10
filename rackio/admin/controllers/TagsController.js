(function(){

  angular
    .module('app')
    .controller('TagsController', [
      '$http',
      '$interval',
      TagsController
    ]);

  function TagsController($http, $interval) {
    
    var vm = this;

    vm.tagsData = [];

    vm.loadTags = function(){
      $http.get('/api/tags', {cache: false})
      .then(function(response){
        vm.tagsData = response.data;
      });
    };

    $interval( function(){ vm.loadTags(); }, 1000);

  }

})();
