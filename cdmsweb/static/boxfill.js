function boxfill(variable, boxfill) {
    // Start asynch requests
    var width = 960, height=960;
    var box_details = utils.getJSON("/vcs/boxfill/" + boxfill);
    var data = variable.axes.then(function(d) {
        var time_axis = d.axisOfType("time");
        if (time_axis === undefined) {
            // We'll just grab the whole thing
            return variable.getTime()
        } else {
            return variable.getTime(time_axis.data[0]);
        }
    });
    var levels = data.then(function(nd) {
        // Get min and max so we can fetch the levels
        var min = null, max = null;
        for (var i = 0; i < nd.buffer.length; i++) {
            if (min == null || nd.buffer[i] < min) {
                min = nd.buffer[i];
            }
            if (max == null || nd.buffer[i] > max) {
                max = nd.buffer[i];
            }
        }
        return utils.getJSON("/vcs/boxfill/" + boxfill + "/levels?min=" + min + "&max=" + max);
    });
    var proj = box_details.then(function(box){
        return utils.getJSON("/vcs/projection/" + box.projection).then(function(d){
            var proj = d3.geo.mercator()
                             .scale((width + 1) / 2 / Math.PI)
                             .translate([width / 2, height / 2])
                             .precision(.1);
            return proj;
        });
    });

    var continents = utils.getJSON("/vcs/continents");
    var colormap = box_details.then(function(box) {
        var cmap_name = "default";
        if (box.colormap !== null) {
            cmap_name = box.colormap;
        }
        return utils.getJSON("/vcs/colormap/" + cmap_name);
    }).then(function(cmap){
        // Convert VCS colors into real colors
        return vcs.colormap(cmap);
    });
    var axes = variable.axes;
    var contexts = vcs.init();

    // Draw data
    var box_plot = Promise.all([box_details, data, levels, colormap, proj, axes]).then(function(values){

        function get_bounds(lon0, lon1, lat0, lat1) {
            var min_lat = axes["latitude"].bounds[lat0][1];
            var max_lat = axes["latitude"].bounds[lat1][0];
            var min_lon = axes["longitude"].bounds[lon0][1];
            var max_lon = axes["longitude"].bounds[lon1][0];
            return {
                x1: min_lon,
                x2: max_lon,
                y1: min_lat,
                y2: max_lat
            }
        }

        function avg_cells(lon0, lon1, lat0, lat1, data) {
            var lonind;
            var latind;
            var value = 0;
            var pct;
            var box_bounds;
            var self_bounds = {
                y1: lat.bounds[lat0][1],
                y2: lat.bounds[lat1][0],
                x1: lon.bounds[lon0][1],
                x2: lon.bounds[lon1][0]
            };
            var self_area = (self_bounds.y2 - self_bounds.y1) * (self_bounds.x2 - self_bounds.x1);
            var count = 0;
            var xcomp, ycomp;
            for (latind = lat0; latind <= lat1; latind++) {
                for (lonind = lon0; lonind <= lon1; lonind++) {
                    value += data.getVal(latind, lonind);
                    count += 1;
                }
            }
            return value / count;
        }
        var boxfill = values[0];
        var data = values[1];
        var levels = values[2];
        var colormap = values[3];
        var projection = values[4];
        var axes = values[5];
        var lat = axes.axisOfType("latitude");
        var lon = axes.axisOfType("longitude");
        var lat_med = vcs.axis_meridian(lat);
        var lon_med = vcs.axis_meridian(lon);
        projection.rotate([lon_med, lat_med, 0]);
        var color_scale = d3.scale.linear()
                                  .domain([0, levels.length])
                                  .rangeRound([boxfill.color_1, boxfill.color_2]);



        var boxes = [];
        var colored = {}
        function rotated_projection_inversion(x, y) {
            point = projection.invert([x, y]);
            if (point[0] < lon.bounds[0][0]) {
                point[0] += 360
            }
            if (point[1] < lat.bounds[0][0]) {
                point[1] += 180;
            }
            return point
        }
        if (960 * 960 < lat.bounds.length * lon.bounds.length) {
            // Merge cells into single pixels...
            for (var y = 0; y < height - 1; y++) {
                lon_ind = 0;
                for (var x = 0; x < width - 1; x++) {
                    lat_ind = 0;
                    box = {};
                    // Find all cells in this pixel
                    // This is the center of the pixel in lat/lon
                    point = rotated_projection_inversion(x, y);
                    // Now we should determine the bounds of this pixel...

                    if (y === 0) {
                        min_lat = lat.bounds[0][0];
                    } else {
                        min_lat = (rotated_projection_inversion(x, y - 1)[1] - point[1]) / 2. + point[1];
                    }

                    if (x === 0) {
                        min_lon = lon.bounds[0][0];
                    } else {
                        min_lon = (rotated_projection_inversion(x - 1, y)[0] - point[0]) / 2 + point[0];
                    }

                    if (x === width - 1) {
                        max_lon = lon.bounds[lon.bounds.length - 1][0];
                    } else {
                        max_lon = (rotated_projection_inversion(x + 1, y)[0] - point[0]) / 2 + point[0];
                    }

                    if (y === height - 1) {
                        max_lat = lat.bounds[lat.bounds.length - 1][1];
                    } else {
                        max_lat = (rotated_projection_inversion(x, y + 1)[1] - point[1]) / 2 + point[1];
                    }

                    // Now find the start and end of the lat/lon ranges
                    while (lat.bounds[lat_ind][1] < min_lat) {
                        lat_ind++;
                    }
                    while (lon.bounds[lon_ind][1] < min_lon) {
                        lon_ind++;
                    }
                    box.start_lat = lat_ind;
                    box.start_lon = lon_ind;

                    while (lat.bounds[lat_ind][0] < max_lat) {
                        lat_ind++;
                    }
                    while (lon.bounds[lon_ind][0] < max_lon) {
                        lon_ind++;
                    }
                    box.end_lat = lat_ind;
                    box.end_lon = lon_ind;
                    box.x1 = x;
                    box.x2 = x + 1;
                    box.y1 = y;
                    box.y2 = y + 1;
                    boxes.push(box);
                }
            }
        } else {
            for (var y = 0; y < lat.bounds.length; y++) {
                for (var x = 0; x < lon.bounds.length; x++) {
                    box = {
                        start_lat: y,
                        start_lon: x,
                        end_lat: y,
                        end_lon: x,
                    };
                    // Bottom left
                    point = projection([lon.bounds[x][0], lat.bounds[y][0]]);
                    box.x1 = point[0];
                    box.y1 = point[1];
                    // Top right
                    point = projection([lon.bounds[x][1], lat.bounds[y][1]]);
                    box.x2 = point[0];
                    box.y2 = point[1];

                    //console.log(y, box.y1, box.y2)
                    boxes.push(box);
                }
            }
        }

        boxes = boxes.map(function(d, ind) {
            d.value = avg_cells(d.start_lon, d.end_lon, d.start_lat, d.end_lat, data);
            var level = vcs.level_of(d.value, levels);
            d.color = "rgba(" + colormap[color_scale(level)].join(",") + ")";
            if (colored[d.color] === undefined) {
                colored[d.color] = [d];
            } else {
                colored[d.color].push(d);
            }
            return d;
        });

        Object.getOwnPropertyNames(colored).map(function(color) {
            contexts.render.fillStyle = color;
            colored[color].map(function(d) {
                contexts.render.fillRect(d.x1, d.y1, d.x2 - d.x1, d.y2 - d.y1);
            });
        });

        vcs.draw_continents(contexts, lat, lon, continents, proj, box_plot);
    });
}