var styles = {
    tadColor:'#CEA04A',
    statusColor:{
        'status-1':'rgba(219,85,85,0.8)',
        'status-2':'rgba(212,162,70,0.8)',
        'status-3':'rgba(204,255,51,0.8)',
        'status-4':'rgba(161,237,68,0.8)',
        'status-complete':'rgba(118,219,85,0.8)',
        'status-none':'rgba(219,217,217,0.6)'
    },
    route:{
        color:'#424559',
        weight:5,
        opacity:1,
        clickable:false
    },
    tadQuota:{
        weight: 1,
        opacity: 1,
        fillOpacity: 1
    },
    tadDefault:{
        fillColor:this.tadColor,
        color:'#595959',
        weight:3,
        dashArray:'2 6',
        opacity:1,
        fillOpacity:0.7
    },
    tadHover:{
        fillColor:'#45A035',
        color:'#595959',
        weight:3,
        opacity:1,
        fillOpacity: 0.2
    },
    _defaultStyle:{
        fillColor:this.tadColor,
        color:'#595959',
        weight:3,
        dashArray:'2 6',
        opacity:1,
        fillOpacity:0.15
    },
    _eventStyle:{
        fillColor:'#536FD6',
        color:'#3F4D96',
        weight:4,
        opacity:1,
        fillOpacity: 0.4
    },

    offCentroid:{
        color:'#06112D',
        fillColor:'#06112D',
        weight:0.5,
        opacity:0.9,
        fillOpacity:0.6
    }
};

var icons = {
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


function BuildStops(MAP_THIS) {
    this.MAP_THIS = MAP_THIS;
}

BuildStops.prototype = {
    pointFunctionStops:function(feature, latlng) { 
        var opt = jQuery.extend(true, {}, styles.tadQuota); 
        opt.fillColor = '#000'; 
        opt.color = '#302D5B';    
        opt.fillOpacity = 0.6
        opt.radius = 4; 
        opt.clickable = false; 
        var marker = new L.circleMarker(latlng, opt); 
        return marker; 
    },
    build:function(data) {
        var stops = [{}, {}];
        var THIS = this;
        $([0, 1]).each(function(index, dir) {
            for(var key in data[dir]) {
                var item = data[dir][key];
                stops[dir][item.tad] = new L.geoJson(item.stops, {
                    pointToLayer:THIS.pointFunctionStops
                });
            }
        });
        return stops;
    }
};

function BuildQuotas(MAP_THIS) {
    this.MAP_THIS = MAP_THIS;
    // '12a-3a', '3a-6a', ... (skip these first two)
    this.tblHeaders = ['', '', '6a-9a','9a-12p','12p-3p','3p-6p','6p-9p','9p-12a'];
}


BuildQuotas.prototype = {
    _buildCell:function(label, pct, header) {
        pct = Math.round(pct);
        var td = $('<td>');
        if(header == true) td = $('<th>');
        if(label) {
            td.attr("class", this._getStatus(pct));
            td.text(label);
            td.attr("align", "center");
        }
        else {
            label = this._getPctText(pct);
            td.attr("class", this._getStatus(pct));
            td.text(label);
            td.attr("align", "center");
        }
        return td;
    },
    _getPctText:function(pct) {
        var text;
        if(pct < 0) text = 'N/A';
        else text = pct.toString() + "%";
        return text;
    },
    _getPct:function(count, quota) {
        if(quota == null) return null;
        if(count == null) return 0;
        return Math.round((count / quota ) * 100);
    },
    _getStatus:function(pctComplete) {
        var cls = "";
        if(pctComplete < 0)
            return "status-none";
        switch (Math.floor(pctComplete / 25) + 1) {
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
    },
    tadPointToLayer:function() {
        var THIS = this;
        return function(feature, latlng) {
            var opt = jQuery.extend(true, {}, styles.tadQuota);
            var code = THIS._getStatus(
                THIS._getPct(feature.properties.count,feature.properties.ons)
            );
            opt.fillColor = styles.statusColor[code];
            opt.fillOpacity = 0.8;
            opt.color = '#565656';   //styles.statusColor[code];
            opt.radius =  Math.log(feature.properties.ons) / Math.log(10) * 10;
            //console.log(opt);
            var marker = new L.circleMarker(latlng, opt);
            return marker;
        }
    },
    buildTadTable:function(properties) {
        console.log("BUILD TABLE");
        console.log(properties);
        var THIS = this;
        var tableDiv = $('<div>')
        if (properties) {
            var row0 = $('<tr>');
            var row1 = $('<tr>');
            var row2 = $('<tr>');
            var row3 = $('<tr>');
            var row4 = $('<tr>');
            var count = Math.round(properties.count);
            var ons = Math.round(properties.ons);
            var pct = (count / ons) * 100;
            var complete = Math.round(pct).toString() + '% ' +
                count + '/' + ons;
            var header = THIS._buildCell(
                'Time of Day - Quotas', pct, true)
                .attr('colspan', '6')
                .css('background-color', 'rgba(255,255,255,0.5)');
            var summaryHeader = THIS._buildCell(
                'Summary: ', pct, true).attr('colspan', '2');
            var summary = THIS._buildCell(complete, pct, true).attr('colspan', '4');
            row0.append(header);
            row4.append(summaryHeader).append(summary);
            
            $(THIS.tblHeaders).each(function(index, item) {
                // skip 12a-3a and 3a-6a
                if(index > 1) {
                    var pct;
                    var feat = properties.time[index - 2];
                    //console.log(feat);
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
                    row1.append(THIS._buildCell(THIS.tblHeaders[index], pct, true));
                    //row1.append(THIS._buildCell(THIS.tblHeaders[index], pct));
                    row2.append(THIS._buildCell(null, pct));
                    row3.append(THIS._buildCell(num_text ,pct));
                }
            });
            //tableDiv.addClass("table-responsive panel panel-default")
            tableDiv.append($('<table>').addClass('quotas-table')
                    .append(row0).append(row1).append(row2).append(row3).append(row4)
                );
        }
        return $('<div>').append(tableDiv.html()).html();
    },
    tadOnEachFeature:function() {
        var THIS = this;
        return function(feature, layer) {
            var tableDiv = THIS.buildTadTable(feature.properties);
            var popup = L.popup({'minWidth':320})
                .setContent(tableDiv);
            layer.bindPopup(popup);
        };
    },
    build:function(data, timeData) {
        var THIS = this;
        var fc = {
            "type":"FeatureCollection",
            "features":[]
        };
        for(var key in data) {
            var item = data[key];
            var tad = key;
            var geo = item.centroid;
            var prop = {
                tad:tad,
                count:item.count,
                ons:item.ons,
                time:timeData[tad]
            };
            geo.properties = prop;
            fc.features.push(geo);
        }
        return new L.geoJson(fc, {
                pointToLayer:THIS.tadPointToLayer(),
                onEachFeature:THIS.tadOnEachFeature()
        });
    },
    buildTables:function(data, timeData) {
        var THIS = this;
        var quotasTables = {};
        for(var key in data) {
            var item = data[key];
            var tad = key;
            var prop = {
                tad:tad,
                count:item.count,
                ons:item.ons,
                time:timeData[tad]
            };
            quotasTables[tad] = $('<div>').append(THIS.buildTadTable(prop));
        }
        return quotasTables;
    }
}





function BuildTads(MAP_THIS) {
    this.MAP_THIS = MAP_THIS;
}

BuildTads.prototype = {
    style:styles.tadDefault,
    mouseover:function() {
        var MAP_THIS = this.MAP_THIS;
        return function(e) {
            var layer = e.target;
            var tad = layer.feature.properties.tad;
            MAP_THIS.manager.curView.triggerEvent(layer, tad);
        }
    },
    build:function(data) {
        var THIS = this;
        var layers = [new L.featureGroup(), new L.featureGroup()];
            $(data).each(function(index, tad) {
                var feature = {
                    "type": "Feature",
                    "properties": {
                        "dir":tad.dir,
                        "tad":tad.tad
                    },
                    "geometry":JSON.parse(tad.geom)
                }
                var tadFeatures = new L.geoJson(feature, {style:THIS.style});
                tadFeatures.eachLayer(function(tad) {
                    tad.addEventListener('mouseover', THIS.mouseover());
                    tad.addEventListener('click', THIS.mouseover());
                });
                layers[tad.dir].addLayer(tadFeatures);
            });
        return layers;
    }
}

function BuildOffs(MAP_THIS) {
    this.MAP_THIS = MAP_THIS;
}

BuildOffs.prototype = {
    style:styles.offCentroid,
    pointToLayer:function() {
        var THIS = this;
        return function(feature, latlng) {
            var opt = jQuery.extend(true, {}, THIS.style);
            var pct = feature.properties.pct;
            opt.radius = Math.log(feature.properties.offs) / Math.log(10) * 15;
            var marker = new L.circleMarker(latlng, opt);
            return marker;
        };
    },
    build:function(summary, offs, geoms) {
        var THIS = this;
        var features = {};
        var fc = {
            "type":"FeatureCollection",
            "features":[]
        };
        $(summary).each(function(index, on_tad) {
            var newFc = jQuery.extend(true, {}, fc);
            //construct feature for centroid of bus stops
            //for each tad
            $(offs[on_tad.tad].offs).each(function(index, off_tad) {
                if(geoms.hasOwnProperty(off_tad.tad)) {
                    var centroid = geoms[off_tad.tad].centroid;
                    var prop = {};
                    prop.tad = off_tad.tad;
                    prop.offs = off_tad.offs;
                    prop.pct = off_tad.offs / on_tad.ons;
                    centroid.properties = prop;
                    newFc.features.push(centroid);
                }
            });
            features[on_tad.tad] = new L.geoJson(newFc, {
                pointToLayer:THIS.pointToLayer()
            });
        });
        return features;
    },
    onTadData:function(summary, offs, geoms) {
        var THIS = this;
        var features = {};
        $(summary).each(function(index, on_tad) {
            features[tad] = on_tad.ons;
        });
        return features;
    },
    /*
    buildPies:function(summary, offs, geoms) { 
        var THIS = this;
        var pies = {};
        var id = 1;
        $(summary).each(function(index, on_tad) {
            $(offs[on_tad.tad].offs).each(function(index, off_tad) {
                var pct = off_tad.offs / on_tad.ons;
                var pct_label = Math.round(pct * 100) + '%';
                // testing using d3 for icons
                var newId = 'pie-' + id;
                id = id + 1;
                var radius = Math.log(off_tad.offs) / Math.log(10) * 15;
                var diameter = radius * 2;
                var svg = document.createElement("svg");
                var svgContainer = d3.select(svg)
                    .attr("id", newId)
                    .attr("width", diameter)
                    .attr("height", diameter);
                var translate = "translate("+radius+","+radius+")";
                var arc = d3.svg.arc()
                    .innerRadius(radius /2)
                    .outerRadius(radius)
                    .startAngle(0)
                    .endAngle(2*Math.PI);
                svgContainer.append("path")
                    .attr("d", arc)
                    .attr("transform", translate);
                console.log($(svg));
                pies[on_tad] = svg;
            });
        });
        return pies 
    },
    */
    buildLabels:function(summary, offs, geoms) {
        var THIS = this;
        var features = {};
        $(summary).each(function(index, on_tad) {
            var labels = new L.featureGroup();
            $(offs[on_tad.tad].offs).each(function(index, off_tad) {
                if(geoms.hasOwnProperty(off_tad.tad)) {
                    var pct = off_tad.offs / on_tad.ons;
                    var centroid = geoms[off_tad.tad].centroid;
                    var pct_label = Math.round(pct * 100) + '%';
                    var table = $('<table>');
                    table.append($('<tr>').append($('<td>').text(pct_label)));
                    table.append($('<tr>').append($('<td>').text(off_tad.offs)));
                    var div = $('<div>').addClass('off-label').append(table);
                    var labelIcon = L.divIcon({
                        html:div[0].outerHTML,
                        className:'',
                        iconAnchor:[15,15]
                    });
                    var label = new L.marker(
                        [centroid.coordinates[1], centroid.coordinates[0]],
                        {icon:labelIcon}
                    );
                    labels.addLayer(label);
                }
            });
            features[on_tad.tad] = labels;
        });
        return features;
    }
}

function BuildRoutes(MAP_THIS) {
    this.MAP_THIS = MAP_THIS;
}

BuildRoutes.prototype = {
    style:styles.route,
    startIcon:icons.start,
    endIcon:icons.end,
    terminusFactory:function (geojson, label, icon) {
        coords = [geojson.coordinates[1], geojson.coordinates[0]]
        return new L.marker(coords, {'icon':icon}).bindLabel(label);
    },
    build:function(routes, terminus) {
        var THIS = this;
        var layers = [{}, {}];
            $([0, 1]).each(function (index, dir) {
                layers[dir].route = new L.geoJson(
                    routes[dir].geom, THIS.style
                );
                layers[dir].start = THIS.terminusFactory(
                    JSON.parse(terminus[dir].start.geom),
                    'START: ' + terminus[dir].start.stop_name,
                    THIS.startIcon
                );
                layers[dir].end = THIS.terminusFactory(
                    JSON.parse(terminus[dir].end.geom),
                    'END: ' + terminus[dir].end.stop_name,
                    THIS.endIcon
                );
            });
        return layers;
    }
}

function Map(args) {
    this.map = this.initmap(args.mapID); 
    this.manager = new ViewManager();
    this.url = args.url;
    this.cog = args.cog;
    this.dirTabs = args.dirTabs;
    this.sidebar = null;
}

Map.prototype = {
    trimetTiles:function() {
        var url = "http://{s}.trimet.org"+
            "/tilecache/tilecache.py/1.0.0/currentOSM/{z}/{x}/{y}";
        return new L.TileLayer(url, {
            minZoom: 8,
            maxZoom: 20,
            attribution:"Map data &copy; 2015 Oregon Metro " +
                "and <a href='http://openstreetmap.org'>OpenStreetMap</a> contributors",
            subdomains:["tilea", "tileb", "tilec", "tiled"]
        });
    },
    osmTiles:function() {
        var url='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
        return new L.TileLayer(url, {
            minZoom: 8,
            maxZoom: 20,
            attribution: 'Map data © '+
            '<a href="http://openstreetmap.org">OpenStreetMap</a>contributors'
        });
    },
    initmap:function(map_div) {
        var map = new L.Map(map_div);
        var tiles = this.trimetTiles()
        map.setView(new L.LatLng(45.5, -122.5),11);
        map.addLayer(tiles);
        return map;
    },
    downloadStatusOn:function() {
        var THIS = this;
        $(THIS.dirTabs).hide();
        $(THIS.cog).show();
    },
    downloadStatusOff:function() {
        var THIS = this;
        $(THIS.cog).hide();
        $(THIS.dirTabs).show();
    },
    activateRoute:function(args) { //cur, rteDesc, activateView) {
        var THIS = this;
        THIS.currentRte = args.active.rte;
        if(!THIS.manager.routeDownloaded(args.active.rte)) {
            THIS.downloadStatusOn();
            THIS.manager.turnOff();
            $.getJSON(this.url, {rte_desc:args.rteDesc}, function(data) {
                console.log(data);
                THIS.manager.addRoute(THIS.currentRte)
                THIS.buildData(data);
                THIS.downloadStatusOff();
                args.activateView(args.active);
            });
        }
        else {
            args.activateView(args.active);
        }
        return true;
    },
    addSidebar:function(sidebar, sidebarID) {
        this.map.addControl(sidebar);
        this.sidebar = $('#'+sidebarID);
    },
    buildData:function(data) {
        var THIS = this;
        var viewArgs = {
            rte:this.currentRte,
            defaultStyle:styles._defaultStyle,
            eventStyle:styles._eventStyle
        };
        function buildViewArgs(viewArgs, dir, viewName, sidebar) {
            var args = jQuery.extend(true, {}, viewArgs);
            args.dir = dir;
            args.viewName = viewName;
            args.sidebar = sidebar;
            return args;
        }
        var viewOffs = {
            0:new View(this.map, buildViewArgs(viewArgs, 0, 'Offs', THIS.sidebar)),
            1:new View(this.map, buildViewArgs(viewArgs, 1, 'Offs', THIS.sidebar))
        };
        var viewQuotas = {
            0:new View(this.map, buildViewArgs(viewArgs, 0, 'Quotas', THIS.sidebar)),
            1:new View(this.map, buildViewArgs(viewArgs, 1, 'Quotas', THIS.sidebar))
        }
        var tads = new BuildTads(THIS);
        var routes = new BuildRoutes(THIS);
        var offs = new BuildOffs(THIS);
        var quotas = new BuildQuotas(THIS);
        var tadStops = new BuildStops(THIS);
        //tadLayer has a hover event handler attached to it
        var tadLayers = tads.build(data.tads);
        var routeLayers = routes.build(data.routes, data.minmax);
        var tadStopLayers = tadStops.build(data.stops);
        $([0, 1]).each(function(index, dir) {
            var quotasLayer = quotas.build(data.stops[dir], data.time_data[dir]);
            var quotasTables = quotas.buildTables(data.stops[dir], data.time_data[dir]);

            var offLabelLayer = offs.buildLabels(
                data.summary[dir],
                data.data[dir],
                data.stops[dir]
            );
            var offLayer = offs.build(
                data.summary[dir],
                data.data[dir],
                data.stops[dir]
            );
            //tad display layer
            viewOffs[dir].addDisplayLayer(tadLayers[dir]);
            viewQuotas[dir].addDisplayLayer(tadLayers[dir]);
            //route and terminus layers
            $(["route", "end", "start"]).each(function(index, layer) {
                viewOffs[dir].addDisplayLayer(routeLayers[dir][layer]);
                viewQuotas[dir].addDisplayLayer(routeLayers[dir][layer]);
            });
            //"Offs" layers
            $([offLayer, offLabelLayer]).each(function(index, layer) {
                for(var key in layer) {
                    viewOffs[dir].addEventLayer(layer[key], key);
                }
            });
            viewQuotas[dir].addDisplayLayer(quotasLayer);
            //tad stops hover layers
            for(var key in tadStopLayers[dir]) {
                viewOffs[dir].addEventLayer(tadStopLayers[dir][key], key);
                viewQuotas[dir].addEventLayer(tadStopLayers[dir][key], key);
            }
            for(var key in quotasTables) {
                viewQuotas[dir].addEventCallback(key, {
                    activate:function(feature, key) {
                        //add html table to map sidebar
                        console.log("active callback hello");
                        $('#map-sidebar').show().append(quotasTables[key]);
                        //$('#map-sidebar').css('display', '').empty()
                        //    .append(quotasTables[key]);
                    },
                    close:function(feature, key) {
                        //remove html table from map sidebar
                        console.log("close callback hello");
                        $('#map-sidebar').empty().hide();
                    }
                });
            }
            //add views to manager
            THIS.manager.addView(viewOffs[dir]);
            THIS.manager.addView(viewQuotas[dir]);
        });
    },
    activateView:function(rte, dir, viewName) {
        this.manager.activateView(rte, dir, viewName);
    }
}

