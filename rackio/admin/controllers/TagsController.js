(function(){

  angular
    .module('app')
    .controller('TagsController', [
      'tableService',
      TagsController
    ]);

  function TagsController(tableService) {
    
    var vm = this;

    vm.tagsData = [];
    
  }

})();
