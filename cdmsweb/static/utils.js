var utils = {
    NDBuffer: function(buff, shape){
        this.buffer = buff;
        this.shape = shape;
        this.getVal = function() {
            var axis_ind = 0;
            if (arguments.length < this.shape.length) {
                return null;
            }
            var value_ind = 0;
            var iterind = 0;
            var multi_val;
            for (axis_ind = 0; axis_ind < this.shape.length; axis_ind++) {
                multi_val = 1;
                for (iterind = axis_ind + 1; iterind < this.shape.length; iterind++) {
                    multi_val *= this.shape[iterind];
                }
                value_ind += multi_val * arguments[axis_ind];
            }
            return this.buffer[value_ind];
        };
    },

    getJSON: function(url) {
        var promise = new Promise(function(resolve, reject){
            var xhr = new XMLHttpRequest();
            xhr.open("GET", url);
            xhr.onload = function(ev) {
                var data = JSON.parse(xhr.responseText);
                resolve(data);
            }
            xhr.onerror = function(ev) {
                reject(Error("Unable to load JSON from " + url));
            }
            xhr.send(null);
        });
        return promise;
    },

    getArray: function(url) {
        var promise = new Promise(function(resolve, reject) {
            var xhr = new XMLHttpRequest();
            xhr.responseType = "arraybuffer"
            xhr.open("GET", url);
            xhr.onload = function(ev) {
                var buffer = xhr.response;
                var headers = xhr.getAllResponseHeaders().split("\r\n").reduce(function(prev, cur) {
                    var key, value;
                    var parts = cur.split(": ");
                    key = parts[0];
                    value = parts[1];
                    prev[key] = value;
                    return prev;
                }, {});
                var dtype = headers["x-cdms-datatype"];
                switch (dtype) {
                    case "float32":
                        buffer = new Float32Array(buffer);
                        break;
                    case "float64":
                        buffer = new Float64Array(buffer);
                        break;
                    case "int32":
                        buffer = new Int32Array(buffer);
                        break;
                    case "int64":
                        buffer = new Int64Array(buffer);
                        break
                    default:
                        buffer = new Int32Array(buffer);
                }
                if (headers["x-cdms-shape"] !== undefined) {
                    var shape = headers["x-cdms-shape"].split(",");
                    shape = shape.map(function(d) { return parseInt(d); });
                    buffer = new utils.NDBuffer(buffer, shape);
                }
                resolve(buffer);
            }

            xhr.onerror = function(ev) {
                reject(Error("Unable to retrieve array from " + url));
            }
            xhr.send(null);
        });
        return promise;
    }
}