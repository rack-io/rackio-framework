schedulizer.factory('admin', ['$http', function($http) {
    var adminApi = {};

    adminApi.getSummary = function(){
    
        $http({
            method: 'GET',
            url: '/api/summary',
            dataType: 'json'
        }).then(function successCallback(response){
            adminApi.summary = response.data;
            }, function errorCallback(error) {
            console.log(error)
        });
    
    };

    adminApi.getTags = function(){
    
        $http({
            method: 'GET',
            url: '/api/tags',
            dataType: 'json'
        }).then(function successCallback(response){
            adminApi.tags = response.data;
            }, function errorCallback(error) {
            console.log(error)
        });
    
    };

    adminApi.getControls = function(){
    
        $http({
            method: 'GET',
            url: '/api/controls',
            dataType: 'json'
        }).then(function successCallback(response){
            adminApi.controls = response.data;
            }, function errorCallback(error) {
            console.log(error)
        });
    
    };

    adminApi.getRules = function(){
    
        $http({
            method: 'GET',
            url: '/api/rules',
            dataType: 'json'
        }).then(function successCallback(response){
            adminApi.rules = response.data;
            }, function errorCallback(error) {
            console.log(error)
        });
    
    };

    adminApi.getAlarms = function(){
    
        $http({
            method: 'GET',
            url: '/api/alarms',
            dataType: 'json'
        }).then(function successCallback(response){
            adminApi.alarms = response.data;
            }, function errorCallback(error) {
            console.log(error)
        });
    
    };

    adminApi.getEvents = function(){
    
        $http({
            method: 'GET',
            url: '/api/events',
            dataType: 'json'
        }).then(function successCallback(response){
            adminApi.events = response.data;
            }, function errorCallback(error) {
            console.log(error)
        });
    
    };

    return adminApi;
}]);