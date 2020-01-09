(function(){

  angular
    .module('app')
    .controller('TagsController', [
      'tagsService',
      '$interval',
      TagsController
    ]);

  function TagsController(tagsService, $interval) {
    
    var vm = this;

    vm.tagsData = [];

    vm.loadTags = function(){
      tagsService.getTags.then(function(response){
        console.log(response.data);
        vm.tagsData = response.data;
      });
    };

    $interval( function(){ vm.loadTags(); }, 2000);

  }

})();
