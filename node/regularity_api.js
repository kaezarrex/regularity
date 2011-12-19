
var router = require('./router');

function f(request, response) {

    response.writeHead(200, {'Content-Type' : 'application/json'});
    response.write(JSON.stringify({_id : '0123456789abcdef'}));
}

router.addEndpoint('PUT', /^\/dash\/start\/?$/, f);

