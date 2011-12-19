#! /usr/bin/env node

var http = require('http'),
    url = require('url'),
    router = require('./router'),
    regularityAPI = require('./regularity_api'),

    server = http.createServer(function(request, response) {
        router.route(request, response)
    });

server.listen(8080, '0.0.0.0');

