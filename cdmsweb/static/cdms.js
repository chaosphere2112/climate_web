
var cdms = {};

cdms.Variable = function(meta_url) {
    var self = this;
    this.ready = utils.getJSON(meta_url).then(function(d){
        self.init(d);
    });
    this.data_url = null;
    this.axes = null;
    this._times = {};
};

cdms.Variable.prototype = {
    init: function(metadata) {
        var self = this;
        this.axes = Promise.all(metadata.axes.map(utils.getJSON))
               .then(function(values){
                    var axes = {};
                    values.map(function(d){
                        axes[d.id] = d;
                    });
                    return new cdms.AxisList(axes);
               });
        this.data_url = metadata.variable;
        return this;
    },
    getTime: function(t) {
        var self = this;
        if (t === undefined) {
            return utils.getArray(this.data_url).then(function(d) {
                return d;
            });
        } else {
            if (this._times[t] !== undefined) {
                // Manufacture a promise for API consistency
                return new Promise(function(resolve) {
                    resolve(self._times[t]);
                });
            }
            return utils.getArray(this.data_url + "?time=" + t).then(function(d){
                self._times[t] = d;
                return d;
            });
        }
    }
};

cdms.AxisList = function(axes) {
    this._obj = axes;
}

cdms.AxisList.prototype = {
    list: function() {
        var list = [];
        var self = this;
        this.ids().map(function(d){
            list.push(self._obj[d]);
        });
        list.sort(function(a, b){
            return a.index - b.index;
        });
        return list;
    },
    ids: function() {
        return Object.getOwnPropertyNames(this._obj);
    },
    axisOfType: function(axis_type) {
        return this.list().filter(function(d) {
            return d.type == axis_type;
        })[0];
    }
}
