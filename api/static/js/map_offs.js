var init = function() {
    //map options
    var status_color = {
        'status-1':'rgba(219,85,85,0.8)',
        'status-2':'rgba(212,162,70,0.8)',
        'status-3':'rgba(204,255,51,0.8)',
        'status-4':'rgba(161,237,68,0.8)',
        'status-complete':'rgba(118,219,85,0.8)',
        'status-none':'rgba(219,217,217,0.6)'
    };
    var red = '#D62020';
    var green = '#26D620';
    var blue = '#2035D6';
    var orange = '#D69020';
    var black =' #000';
    var grey_blue = '#424559';
    var dark_blue = '#2E3B5E';
    var options = {
        radius: 8,
        color: black,
        weight: 1,
        opacity: 1,
        fillOpacity: 1
    };
    var icon = {
        start: L.icon({
            iconUrl: '../static/icons/bus-12-green.svg',
            iconSize: [30, 30],
            iconAnchor: [18, 18],
            popupAnchor: [0, -18],
            labelAnchor: [14, 0]
        }),
        end: L.icon({
            iconUrl: '../static/icons/bus-12-red.svg',
            iconSize: [30, 30],
            iconAnchor: [18, 18],
            popupAnchor: [0, -18],
            labelAnchor: [14, 0]
        })
    };

    // variables
    //var tbl_headers = ['', '', '6a-9a','9a-12p','12p-3p','3p-6p','6p-9p','9p-12a'];
    var layer_names = ['tads', 'route', 'start', 'end'];
    var layers = {
        1:{
            'tads':null,
            'route':null,
            'start':null,
            'end':null
        },
        0:{
            'tads':null,
            'route':null,
            'start':null,
            'end':null
        }
    };
    var active = null;
    var active_hover = null;
    var active_tad = null;
    //var active_dir = null;
    //var active_tad = null;

    var hover_data = {};
    hover_data[0] = {};
    hover_data[1] = {};
    //data = {
    //  0:{'0000012':new L.geojson(), ... },
    //  1:{'0000012':new L.geojson(), ... }
    //};
    //var stops;
    //var tad_stops = {};
    var map = initmap('map');

    $('#filter_line a').on('click', function() {
        var dir = dir_lookup[this.text];
        var args = {"rte_desc":this.text};
        
        $('#dir-tabs li.disabled').removeClass('disabled');
        $("#line-btn").text(this.text+' ').append('<span class="caret"></span>');
        $("#outbound-link > a").text(dir[0]);
        $("#inbound-link > a").text(dir[1]);
        $('#outbound-link').removeClass('active');
        $('#inbound-link').addClass('active');
        
        //fetch route stats
        $.getJSON('map_offs/_details', args, function(data) {
            console.log(data);
            turnoff_dir();
            
            hover_data[0] = build_tad_hover_feature(
                data.summary[0], data.data[0], data.stops[0]);
            hover_data[1] = build_tad_hover_feature(
                data.summary[1], data.data[1], data.stops[1]);
            console.log(hover_data[0]);
            console.log(hover_data[0]['00000101']);
            //hover_data[0]['00000101'].addTo(map);

            //hover_data[0]['00000114'].addTo(map);
            
            var tadStyleOptions = {
                fillColor: 'black', //blue,
                color: '#595959', //blue,
                weight: 3,
                dashArray:'2 6',
                opacity: 1,
                fillOpacity: 0.15
            };

            var fg = {0:new L.featureGroup(), 1:new L.featureGroup()};
            
            var tadStyle = function(feature) {
                return tadStyleOptions;
            }

            function mouseoutTAD(e) {}

            var hoverTADStyle = {
                fillColor: '#555C91', //blue,
                color: '#595959', //blue,
                weight: 3,
                //dashArray:'2 6',
                opacity: 1,
                fillOpacity: 0.6
            };
            

            var tadExists = function(dir, tad) {
                var ret_val = false;
                if(hover_data.hasOwnProperty(dir)) {
                    if(hover_data[dir].hasOwnProperty(tad)) {
                        ret_val = true;
                    }
                }
                return ret_val;
            }


            function mouseoverTAD(e) {
                var layer = e.target;
                var dir = layer.feature.properties.dir;
                var tad = layer.feature.properties.tad;
                if(tadExists(dir, tad)) {
                    if(active_tad == null) {
                        active_hover = hover_data[dir][tad];
                        active_tad = layer;
                        map.addLayer(active_hover);
                        active_tad.setStyle(hoverTADStyle);
                    }
                    else {
                        if(active_tad != layer) {
                            active_tad.setStyle(tadStyleOptions);
                            map.removeLayer(active_hover);
                            active_hover = hover_data[dir][tad];
                            active_tad = layer;
                            layer.setStyle(hoverTADStyle);
                            map.addLayer(active_hover);
                        }
                    }
                }
            }

            function eachTAD(feature, layer) {
                layer.on({
                    mouseover:mouseoverTAD,
                    mouseout:mouseoutTAD
                });
            }
            
            $(data.tads).each(function(index, tad) {
                var feature = {
                    "type": "Feature",
                    "properties": {
                        "dir":tad.dir,
                        "tad":tad.tad
                    },
                    "geometry":JSON.parse(tad.geom)
                }
                fg[tad.dir].addLayer(new L.geoJson(
                    feature, 
                    {
                        style:tadStyle,
                        onEachFeature:eachTAD
                    }
                ));
            });
            layers[0].tads = fg[0];
            layers[1].tads = fg[1];
            //route geometry
            var route_opt = jQuery.extend(true, {}, options);
            route_opt.color = grey_blue;
            route_opt.weight = 5;
            route_opt.clickable = false;
            delete route_opt.radius;
            $([0, 1]).each(function(index, item) {
                layers[item].route = new L.geoJson(data.routes[item].geom, route_opt);
                console.log(data.minmax[item]);
                layers[item].start = markerFactory(
                    JSON.parse(data.minmax[item].start.geom),
                    'START: ' + data.minmax[item].start.stop_name,
                    icon.start
                );
                layers[item].end = markerFactory(
                    JSON.parse(data.minmax[item].end.geom),
                    'END: ' + data.minmax[item].end.stop_name,
                    icon.end
                );
            });
            turnon_dir(1);
        }); 
    });

    function markerFactory(geojson, label, icon) {
        coords = [geojson.coordinates[1], geojson.coordinates[0]]
        return new L.marker(coords, {'icon':icon}).bindLabel(label);
    }

    function turnoff_dir() {
        if(active != null) {
            $(layer_names).each(function(index, item) {
                map.removeLayer(layers[active][item]);
            });
        } 
        active = null;
    }

    function turnon_dir(dir) {
        if(active != null) turnoff_dir();
        map.addLayer(layers[dir].route);
        map.addLayer(layers[dir].tads);
        map.addLayer(layers[dir].start);
        map.addLayer(layers[dir].end);
        map.fitBounds(layers[dir].route.getBounds());
        active = dir;
    }

    function show_stops(tad) {
        map.addLayer(tad_stops[tad]);
    }

    function hide_stops(tad) {
        map.removeLayer(tad_stops[tad]);
    }

    
    function build_tad_hover_feature(summary, offs, geoms) {
        var ret_val = {};
        var fc = {
            "type":"FeatureCollection",
            "features":[]
        };
        //for each tad in summary for 
        $(summary).each(function(index, on_tad) {
            var new_fc = jQuery.extend(true, {}, fc);
            //construct feature for centroid of bus stops
            //for each tad
            $(offs[on_tad.tad].offs).each(function(index, off_tad) {
                if(geoms.hasOwnProperty(off_tad.tad)) {
                    var pct = off_tad.offs / on_tad.ons;
                    var centroid = geoms[off_tad.tad].centroid;
                    var stops_geom =  geoms[off_tad.tad].stops_geom;
                    
                    
                    var prop = {};
                    prop.tad = off_tad.tad;
                    prop.offs = off_tad.offs;
                    prop.pct = pct;
                    centroid.properties = prop;
                    new_fc.features.push(centroid);
                }
            });
            ret_val[on_tad.tad] = new L.geoJson(new_fc, {
                pointToLayer:pointFunctionTADCentroid
            });
        });
        return ret_val;
    }
    
    function build_dir_feature(data, time_data) {
        var fc = {
            "type":"FeatureCollection",
            "features":[]
        };
        $(data).each(function(index, item) {
            var geo = JSON.parse(item.centroid);
            var prop = {};
            prop.tad = item.tad;
            prop.count = item.count;
            prop.ons = item.ons;
            prop.time = time_data[item.tad];
            geo.properties = prop;
            fc.features.push(geo);
            tad_stops[item.tad] = new L.geoJson(JSON.parse(item.stops), {
                pointToLayer:pointFunctionStops
            });
        });
        return new L.geoJson(fc, {
            pointToLayer:pointFunctionTads,
            onEachFeature:onEachFeature 
        });
    }

    $('#dir-tabs > li > a').click( function() {
        $('#dir-tabs > li.active').removeClass('active');
        $(this).parent().addClass('active');
        var link = $(this).parent().attr('id');
        if(link == 'outbound-link') turnon_dir(0);
        if(link == 'inbound-link') turnon_dir(1);
    });
        
    $(directions).each(function(index, item) {
        if(!dir_lookup.hasOwnProperty(item.rte_desc)) {
            dir_lookup[item.rte_desc] = {};
        }
        dir_lookup[item.rte_desc][item.dir] = item.dir_desc;
    });

    function get_pct_text(pct) {
        var text;
        if(pct < 0) text = 'N/A';
        else text = pct.toString() + "%";
        return text;
    }

    function build_cell(label, pct) {
        pct = Math.round(pct);
        var td = $('<td>'); 
        if(label) {
            td.attr("class", get_status(pct));
            td.text(label);
            td.attr("align", "center");
        }
        else {
            label = get_pct_text(pct);
            td.attr("class", get_status(pct));
            td.text(label);
            td.attr("align", "center");
        }
        return td;
    }
        
    function get_pct(count, quota) {
        if(quota == null) return null;
        if(count == null) return 0;
        return Math.round((count / quota ) * 100);
    }

    function get_status(pct_complete) {
        var cls = "";
        if(pct_complete < 0)
            return "status-none";
        switch (Math.floor(pct_complete / 25) + 1) {
            case 1: //0% -> 24%
                cls = "status-1"; break;
            case 2: //25% -> 49%
                cls = "status-2"; break;
            case 3: //50% -> 74%    
                cls = "status-3"; break;
            case 4: //75% -> 99%    
                cls = "status-4"; break;
            default: //100% +    
                cls = "status-complete";
        }
        return cls;
    }

    var pointFunctionStops = function (feature, latlng) {
        var opt = jQuery.extend(true, {}, options);
        opt.fillColor = blue;
        opt.radius = 4;
        opt.clickable = false;
        var marker = new L.circleMarker(latlng, opt);
        return marker;
    }


    var pointFunctionTADCentroid = function (feature, latlng) {
        var opt = jQuery.extend(true, {}, options);
        var pct = feature.properties.pct;
        var opacity = feature.properties.pct;
       
        console.log(feature);
        function float2color( percentage ) {
            var color_part_dec = 255 * percentage;
            var color_part_hex = Number(parseInt( color_part_dec , 10)).toString(16);
            return "#" + color_part_hex + color_part_hex + color_part_hex;
        }
        
        // grey scale based on pct
        opt.color = '#06112D';
        opt.opacity = 1; //opacity;
        opt.fillColor = '#06112D';
        opt.fillOpacity = 0.7; //opacity;
        opt.radius = Math.log(feature.properties.offs) / Math.log(10) * 20;
       

        /*
        // grey scale based on pct
        opt.color = float2color(pct); //'#06112D';
        opt.opacity = 1; //opacity;
        opt.fillColor = float2color(pct); //'#06112D';
        opt.fillOpacity = 0.7; //opacity;
        opt.radius = 30;
        */

        // status_color[code];
        //opt.radius = pct * 100; //Math.log(feature.properties.offs) / Math.log(10) * 20;
        //opt.radius =  Math.log(feature.properties.ons) / Math.log(10) * 10;
        var marker = new L.circleMarker(latlng, opt);
        //marker.on('mouseover', function(e) {
        //    console.log(marker);
        //    console.log(e);
        //    var feature = e.target.feature.geometry;
        //    show_stops(feature.properties.tad);
        //    marker.openPopup();
        //    marker.options.color = blue;
        //});
        //marker.on('mouseout', function(e) {
        //    var feature = e.target.feature.geometry;
        //    hide_stops(feature.properties.tad);
        //    marker.closePopup();
        //    marker.options.color = black;
        //});
        return marker;
    }


    var pointFunctionTads = function (feature, latlng) {
        var opt = jQuery.extend(true, {}, options);
        var code = get_status(get_pct(
            feature.properties.count,
            feature.properties.ons
        ));
        opt.fillColor = status_color[code];
        opt.radius =  Math.log(feature.properties.ons) / Math.log(10) * 10;
        var marker = new L.circleMarker(latlng, opt);
        marker.on('mouseover', function(e) {
            console.log(marker);
            console.log(e);
            var feature = e.target.feature.geometry;
            show_stops(feature.properties.tad);
            marker.openPopup();
            marker.options.color = blue;
        });
        marker.on('mouseout', function(e) {
            var feature = e.target.feature.geometry;
            hide_stops(feature.properties.tad);
            marker.closePopup();
            marker.options.color = black;
        });
        return marker;
    }

    /*
    // too complicated function to build table for tad centroid
    // popup. Contains different colored column for each three hour
    // period from 6 am to 12 pm (6 columns)
    // if ons is empty column is greyed with a 'N/A' label
    var onEachFeature = function (feature, layer) {
        if (feature.properties) {
            var row1 = $('<tr>'); 
            var row2 = $('<tr>');
            var row3 = $('<tr>');
            var count = Math.round(feature.properties.count);
            var ons = Math.round(feature.properties.ons);
            var pct = (count / ons) * 100;
            var complete = Math.round(pct).toString() + '% ' +
                count + '/' + ons;
            var cell = build_cell(complete, pct).attr('colspan', '6');
            var row4 = $('<tr>').append(cell);
            $(tbl_headers).each(function(index, item) {
                if(index > 1) {
                    var pct;
                    var feat = feature.properties.time[index];
                    var num_text = 'N/A';
                    if(feat) {
                        if(!feat.ons) pct = -1;
                            else if(!feat.count) {
                                num_text = 0 + '/' + Math.round(feat.ons);
                                pct = 0;
                            }
                            else {
                                pct = (feat.count / feat.ons) * 100;
                                num_text = Math.round(feat.count) + '/' + 
                                    Math.round(feat.ons);
                            }
                        }
                    else pct = -1;
                    row1.append(build_cell(tbl_headers[index], pct));
                    row2.append(build_cell(null, pct));
                    row3.append(build_cell(num_text ,pct));
                }
            });
            var popup_html = $('<div>')
                .addClass("table-responsive panel panel-default")
                .append(
                    $('<table>').addClass('table')
                        .append(row1)
                        .append(row2)
                        .append(row3)
                        .append(row4)
                ).html();
            var popup = L.popup({'minWidth':320})
                .setContent(popup_html);
            layer.bindPopup(popup);
        }
    }
    */
}


