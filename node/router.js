
var endpoints = [];

/*
 * Add the endpoint to the router
 */
function addEndpoint(method, pattern, handler) {
    endpoints.push({
        method : method,
        pattern : pattern,
        handler : handler
    });
}

/*
 * Route to the url
 */
function route(request, response) {
    var method = request.method,
        url = request.url,
        validEndpoint = endpoints.some(function(endpoint) {

        var match = endpoint.pattern.exec(url),
            args;

        if (match && method === endpoint.method) {
            // add any arguments present in the url to the method call
            args = [request, response];
            Array.prototype.push.apply(args, match.slice(1));
            endpoint.handler.apply(endpoint, args);

            return true;
        } 

        return false;
    });

    if (!validEndpoint) {
        response.writeHead(404);
    }
    
    console.log(url);
    response.end();
}

exports.addEndpoint = addEndpoint;
exports.route = route;

