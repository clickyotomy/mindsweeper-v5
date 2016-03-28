function xdr(url, method, data, callback, errback) {
    var req;

    if(XMLHttpRequest) {
        req = new XMLHttpRequest();
        if('withCredentials' in req) {
            req.open(method, url, true);
            req.onerror = errback;
            req.onreadystatechange = function() {
                if (req.readyState === 4) {
                    if (req.status >= 200 && req.status < 400) {
                        callback(req.responseText);
                    } else {
                        var whoops = 'Whoops, ' + url + ' returned a ' +
                                     req.status + '! Looks like this ' +
                                     'request will be stuck in here. ' +
                                     'Better start debugging!'
                        errback(new Error(whoops));
                    }
                }
            };
            req.send(data);
        }
    } else if(XDomainRequest) {
        req = new XDomainRequest();
        req.open(method, url);
        req.onerror = errback;
        req.onload = function() {
            callback(req.responseText);
        };
        req.send(data);
    } else {
        var nope = 'Nope! Need cross origin request sharing.'
        errback(new Error(nope));
    }
}

function throwCallback(obfuscated_text) {
    var data = JSON.stringify({'obfuscated': obfuscated_text});
    xdr('/throw', 'POST', data, redirectCallback, ErrorCallback);
}

function redirectCallback(response) {
    redirect = JSON.parse(response)['redirect']
    window.location.replace(redirect);
}

function trigger(username, gist) {
    url = 'https://gist.githubusercontent.com/'+ username + '/' + gist + '/raw';
    xdr(url, 'GET', null, throwCallback, ErrorCallback);
}

function ErrorCallback(message) {
    console.log(message);
}
