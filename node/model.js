
var mongoDb = require('mongodb'),
    utils = require('./utils');

/**
 * Helper function for building an event object to be saved to the database.
 *
 * @param timelineName : String
 *     the name of the timeline to scan for overlapping activities
 * @param name : String
 *     the name of the activity to create
 * @param start : Date
 *     the start time of the activity, in UTC
 * @param end : Date
 *     the end time of the activity, in UTC
 */
function buildEvent(timelineName, name, start, end) {
    return {
        timeline : timelineName,
        name : name,
        start : start,
        end : end
    };
}

function Model() {
    dbServer = new mongoDb.Server('localhost', 27017, {}),
    db = new mongoDb.Db('regularity', dbServer, {
        native_parser : true
    });

    this.db = db;
}

Model.prototype = {

    find : function(query, callback) {
        this.db.open(function(error, db) {
            db.collection('events', function(error, collection) {
                collection.find(query, function(error, cursor) {
                    cursor.toArray(function(error, data) {
                        callback(data);
                        db.close();
                    });
                });
            });
        });
    },

    /** 
     * Return timeline events that overlap with the time denoted by start and 
     * end.
     *  
     *  @param start : Date
     *      the start time of the activity
     *  @param end : Date
     *      the end time of the activity
     *  @param buffer : optional, int
     *      the number of seconds to buffer out the time range, useful for 
     *      catching events that barely don't overlap, defaults to 5 seconds
     *  @param extraCriteria : optional, Object
     *      additional criteria for the query
     */
    overlapping : function(start, end, buffer, extraCriteria, callback) {
        if (!buffer) {
            buffer = 0;
        }

        if (!extraCriteria) {
            extraCriteria = {}
        }

        console.log(start);
        console.log(end);
        console.log(buffer);
        console.log(extraCriteria);

        start = utils.dateAdd(start, -buffer);
        end = utils.dateAdd(end, buffer);

        criteria = extraCriteria;
        criteria['$nor'] = [
            { 'start' : { '$gt' : end } },
            { 'end' : { '$lt' : start } }
        ];

        this.find(criteria, callback);
    }
};

exports.Model = Model;

