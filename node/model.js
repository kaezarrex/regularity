
var mongoDb = require('mongodb');

function Model() {
    dbServer = new mongoDb.Server('localhost', 27017, {}),
    db = new mongoDb.Db('regularity', dbServer, {
        native_parser : true
    });

    this.db = db;
}

Model.prototype = {

    query : function() {
        this.db.open(function(error, db) {
            db.close();
        });
    }

};

/*
db.open(function(error, db) {
    
    db.collection('events', function(error, collection) {
        collection.count(function(error, count) {
            console.log('there are ' + count + ' events.');

        });
    });

    db.close();
});
*/

