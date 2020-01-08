(function(){

  angular
    .module('app')
    .controller('TagsController', [
      'tagsService',
      TagsController
    ]);

  function TagsController(tagsService) {
    
    var vm = this;

    tagsService.getTags.then(function(response){
      console.log(response.data);
    });

    vm.tagsData = [];

  }

})();
