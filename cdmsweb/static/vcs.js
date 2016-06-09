var vcs = {
    init: function() {
        var canvas = document.getElementById("canvas");
        var continent_canvas = document.getElementById("continents");

        canvas.width = 960;
        canvas.height = 960;
        continent_canvas.width = 960;
        continent_canvas.height = 960;

        var context = canvas.getContext("2d");
        var continent_context = continent_canvas.getContext("2d");

        return {"render": context, "continents": continent_context};
    },
    colormap: function(vcs_cmap) {
        var html_colors = [];
        var vcs_color;
        var transform = d3.scale.linear()
                                .domain([0, 100])
                                .rangeRound([0, 255]);
        for (var i = 0; i<256; i++) {
            vcs_color = vcs_cmap.index.data["" + i];
            html_colors.push(vcs_color.map(transform));
        }
        return html_colors;
    },
    draw_continents: function(contexts, lat, lon, continents, proj, plot_promise) {
        var width = 960, height= 960;
        Promise.all([continents, proj, plot_promise]).then(function(values){
            var continents = values[0];
            var proj = values[1];

            contexts.continents.strokeStyle = "#000";
            contexts.continents.lineWidth = 1;
            contexts.continents.beginPath();

            var lat_med = lat.data[Math.floor(lat.length / 2)];
            var lon_med = lon.data[Math.floor(lon.length / 2)];
            continents.map(function(d){
                var point = proj(d[0]);
                contexts.continents.moveTo(point[0], point[1]);
                var last_pos = null;
                d.map(function(data) {
                    var projected = proj(data);
                    if (last_pos !== null) {
                        // Lines probably aren't stretching across the entire canvas...
                        if (Math.sqrt(Math.pow(projected[0] - last_pos[0], 2) + Math.pow(projected[1] - last_pos[1], 2)) > Math.max(width / 2, height/2)) {
                            contexts.continents.moveTo(projected[0], projected[1]);
                        }
                    }
                    contexts.continents.lineTo(projected[0], projected[1]);
                    last_pos = projected;
                });
            });
            contexts.continents.stroke();
        });
    },
    axis_meridian: function(axis) {
        // Returns the centerpoint of the axis
        var median = Math.floor(axis.length / 2);
        var is_even = axis.length % 2 == 0;
        if (is_even) {
            return axis.bounds[median][0]
        } else {
            // Use the bounding point between left and right
            return axis.data[median];
        }
    },
    projection: function(vcsproj) {
        var proj;
        switch (vcsproj.type) {
            case 'linear':
                proj = vcs.geo.equirectangular();
                break;
            case 'albers equal area':
                proj = vcs.geo.albers();
                break;
            case 'lambert':
                proj = vcs.geo.conicConformal();
                break;
            case 'mercator':
                proj = d3.geo.mercator();
                break;
            case 'polyconic':
                proj = d3.geo.polyconic();
                break;
            case 'equid conic a':
                proj = d3.geo.conicEquidistant();
                break;
            case 'transverse mercator':
                proj = d3.geo.transverseMercator();
                break;
            case 'stereographic':
                proj = d3.geo.stereographic();
                break;
            case 'lambert azimuthal':
                proj = d3.geo.azimuthalEqualArea();
                break;
            case 'gnomonic':
                proj = d3.geo.gnomonic();
                break;
            case 'orthographic':
                proj = d3.geo.orthographic();
                break;
            case 'sinusoidal':
                proj = d3.geo.sinusoidal();
                break;
            case 'equirectangular':
                proj = d3.geo.equirectangular();
                break;
            case 'miller':
                proj = d3.geo.miller();
                break;
            case 'van der grinten':
                proj = d3.geo.vanDerGrinten();
                break;
            case 'robinson':
                proj = d3.geo.robinson();
                break;
            case 'mollweide':
                proj = d3.geo.mollweide();
                break;
            case 'wagner iv':
                proj = d3.geo.wagner4();
                break;
            case 'wagner vii':
                proj = d3.geo.wagner7();
                break;
            case 'space oblique':
            case 'alaska':
            case 'interrupted mollweide':
            case 'hammer':
            case 'state plane':
            case 'oblated':
            case 'utm':
            case 'hotin':
            case 'azimuthal':
            case 'polar':
            case 'interrupted goode':
            case 'gen. vert. near per':
                break;
        }
    },
    level_of: function(val, levs) {
        function bin_search(val, levs, start, end) {

            while (start != end) {
                mid = Math.floor((end - start) / 2) + start;
                if (val < levs[mid]) {
                    end = mid;
                    continue;
                }
                if (val > levs[mid]) {
                    start = mid + 1;
                    continue;
                }
                break;
            }

            if (start == end) {
                return start - 1;
            } else {
                return mid;
            }
        }
        return bin_search(val, levs, 0, levs.length);
    }
}