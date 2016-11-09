define(['jquery'], function ($) {
    "use strict";
    
    var url_path_join = function () {
        // join a sequence of url components with '/'
        var url = '', i = 0;

        for (i = 0; i < arguments.length; i += 1) {
            if (arguments[i] === '') {
                continue;
            }
            if (url.length > 0 && url[url.length-1] !== '/') {
                url = url + '/' + arguments[i];
            } else {
                url = url + arguments[i];
            }
        }
        url = url.replace(/\/\/+/, '/');
        return url;
    };
    
    var update = function (d1, d2) {
        // Transfers the keys from d2 to d1. Returns d1
        $.map(d2, function (i, key) {
            d1[key] = d2[key];
        });
        return d1;
    };
    
    var encode_uri_components = function (uri) {
        // encode just the components of a multi-segment uri,
        // leaving '/' separators
        return uri.split('/').map(encodeURIComponent).join('/');
    };
    
    var parse_url = function (url) {
        // an `a` element with an href allows attr-access to the parsed segments of a URL
        // a = parse_url("http://localhost:8888/path/name#hash")
        // a.protocol = "http:"
        // a.host     = "localhost:8888"
        // a.hostname = "localhost"
        // a.port     = 8888
        // a.pathname = "/path/name"
        // a.hash     = "#hash"
        var a = document.createElement("a");
        a.href = url;
        return a;
    };

    var API = (function () {
        // Object representing the interface to the Web API.
        // @param base_url : the url at which to find the web API endpoint.
        var self = {};
        self.base_urlpath = "{{ base_urlpath }}";
        self.default_options = {
            contentType: "application/json",
            cache: false,
            dataType : null,
            processData: false,
            success: null,
            error: null
        };
        
        self.request = function (req_type, endpoint, body) {
            // Performs a request to the final endpoint
            var options = {};
            update(options, self.default_options);
            update(options, {
                type: req_type,
                data: body
            });
            
            var url = url_path_join(
                    self.base_urlpath, 
                    "api", "{{ api_version }}",
                    encode_uri_components(endpoint)
                )+'/';

            console.log("requesting "+url);
            return $.ajax(url, options);
        };
        return self;
    })();

    var Resource = function(type) {
        this.type = type;
        
        this.create = function(representation) {
            var body = JSON.stringify(representation);
            var promise = $.Deferred();

            API.request("POST", type, body)
                .done(function(data, textStatus, jqXHR) {
                    var status = jqXHR.status;
                    
                    var payload = null;
                    try {
                        payload = JSON.parse(data);
                    } catch (e) {
                        // Suppress any syntax error and discard the payload
                    }

                    if (status !== 201) {
                        // Strange situation in which the call succeeded, but
                        // not with a 201. Just do our best.
                        console.log(
                            "Create succeded but response with status " +
                            status + 
                            " instead of 201."
                        );
                        promise.reject(status, payload);
                        return;
                    }
                    
                    var id, location;
                    try {
                        location = jqXHR.getResponseHeader('Location');
                        var url = parse_url(location);
                        var arr = url.pathname.replace(/\/$/, "").split('/');
                        id = arr[arr.length - 1];
                    } catch (e) {
                        console.log("Response had invalid or absent Location header");
                        promise.reject(status, payload);
                        return;
                    }
                    promise.resolve(id, location);
                })
                .fail(function(jqXHR, textStatus, error) {
                    var status = jqXHR.status;
                    var payload = null;
                    try {
                        payload = JSON.parse(jqXHR.responseText);
                    } catch (e) {
                        // Suppress any syntax error and discard the payload
                    }

                    promise.reject(status, payload);
                });
            
            return promise;
            
        };

        this.delete = function(id) {
            var promise = $.Deferred();
            
            API.request("DELETE", url_path_join(type, id))
                .done(function(data, textStatus, jqXHR) {
                    var status = jqXHR.status;
                    var payload = null;
                    try {
                        payload = JSON.parse(data);
                    } catch (e) {
                        // Suppress any syntax error and discard the payload
                    }
                    
                    if (status !== 204) {
                        console.log(
                            "Delete succeded but response with status " +
                            status +
                            " instead of 204."
                        );
                        promise.reject(status, payload);
                        return; 
                    }
                    promise.resolve();
                })
                .fail(function(jqXHR, textStatus, error) { 
                    var status = jqXHR.status;
                    var payload = null;
                    try {
                        payload = JSON.parse(jqXHR.responseText);
                    } catch (e) {
                        // Suppress any syntax error and discard the payload
                    }
                    promise.reject(status, payload);
                });
            
            return promise;
        };

        this.retrieve = function(id) {
            var promise = $.Deferred();
            
            API.request("GET", url_path_join(type, id))
                .done(function(data, textStatus, jqXHR) {
                    var status = jqXHR.status;
                    
                    var payload = null;
                    try {
                        payload = JSON.parse(jqXHR.responseText);
                    } catch (e) {
                        // Suppress any syntax error and discard the payload
                    }

                    if (status !== 200) {
                        console.log(
                            "Retrieve succeded but response with status " +
                            status +
                            " instead of 200."
                        );
                        promise.reject(status, payload);
                        return;
                    }
                        
                    if (payload === null) {
                        console.log(
                            "Retrieve succeded but empty or invalid payload"
                        );
                        promise.reject(status, payload);
                        return;
                    }
                        
                    promise.resolve(payload);
                })
                .fail(function(jqXHR, textStatus, error) {
                    var status = jqXHR.status;
                    var payload = null;
                    console.log(JSON.stringify(jqXHR));
                    console.log(textStatus);
                    console.log(error);
                    try {
                        payload = JSON.parse(jqXHR.responseText);
                    } catch (e) {
                        // Suppress any syntax error and discard the payload
                    }
                    promise.reject(status, payload);
                });
            
            return promise;
        };

        this.items = function() {
            var promise = $.Deferred();
            
            API.request("GET", type)
                .done(function(data, textStatus, jqXHR) {
                    var status = jqXHR.status;

                    var payload = null;
                    try {
                        payload = JSON.parse(jqXHR.responseText);
                    } catch (e) {
                        // Suppress any syntax error and discard the payload
                    }

                    if (status !== 200) {
                        console.log(
                            "Items retrieve succeded but response with status " +
                            status +
                            " instead of 200."
                        );
                        promise.reject(status, payload);
                        return;
                    }

                    if (payload === null) {
                        console.log(
                            "Items Retrieve succeded but empty or invalid payload"
                        );
                        promise.reject(status, payload);
                        return;
                    }
                    promise.resolve(payload.items);
                    
                })
                .fail(function(jqXHR, textStatus, error) {
                    var status = jqXHR.status;
                    var payload = null;
                    try {
                        payload = JSON.parse(jqXHR.responseText);
                    } catch (e) {
                        // Suppress any syntax error and discard the payload
                    }
                    promise.reject(status, payload);
                });
            
            return promise;
        };
    };

    return {
        {% for res in resources %}"{{ res['class_name'] }}" : new Resource("{{ res['collection_name'] }}"),
        {% end %} };
});

