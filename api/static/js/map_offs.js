var styles = {
    route:{
        color:'#424559',
        weight:5,
        opacity:1,
        clickable:false
    },
    tadDefault:{
        fillColor:'black',
        color:'#595959',
        weight:3,
        dashArray:'2 6',
        opacity:1,
        fillOpacity:0.15
    },
    tadHover:{
        fillColor:'#45A035',
        color:'#595959',
        weight:3,
        opacity:1,
        fillOpacity: 0.5
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

function HoverLayers(map) {
    this.map = map;
    this.hoverKey = null;
    this.hoverFeature = null;
    this.layers = {}
    this.namedLayers = {};
}

HoverLayers.prototype = {
    turnoff:function() {
        if(this.hoverKey != null) {
            this.map.removeLayer(this.layers[this.hoverKey]);
            this.hoverFeature.setStyle(styles.tadDefault);
        }
        this.hoverKey = null;
        this.hoverFeature = null;
    },
    update:function(feature, key) {
        if(this.hoverKey == key) return;
        if(!this.layers.hasOwnProperty(key)) return;
        if(this.hoverKey != null) {
            this.hoverFeature.setStyle(styles.tadDefault);
            this.map.removeLayer(this.layers[this.hoverKey]);
        }     
        feature.setStyle(styles.tadHover);
        this.map.addLayer(this.layers[key]);
        this.hoverKey = key;
        this.hoverFeature = feature;
    },
    addLayer:function(layer, label) {
        for(var key in layer) {
            if(!this.layers.hasOwnProperty(key)) {
                this.layers[key] = new L.layerGroup();
                this.namedLayers[key] = {};
            }
            this.layers[key].addLayer(layer[key]);
            this.namedLayers[key][label] = layer[key]
        }
    }
}

function DirectionLayers(map) {
    this.map = map;
    this.activeDir = null;
    this.namedLayers = {0:{},1:{}};
    this.layers = [new L.layerGroup(), new L.layerGroup()];
    this.hoverLayers = [new HoverLayers(this.map), new HoverLayers(this.map)];
}

DirectionLayers.prototype = {
    reset:function() {
        this.turnOff();
        this.namedLayers = {0:{},1:{}};
        this.layers = [new L.layerGroup(), new L.layerGroup()];
        this.hoverLayers = [new HoverLayers(this.map), new HoverLayers(this.map)];
    },
    setDir:function(direction) {
        this.direction = direction;
    },
    addLayer:function(dir, layer, label) {
        this.layers[dir].addLayer(layer);
        this.namedLayers[dir][label] = layer;
    },
    addHoverLayer:function(dir, layer, label) {
        this.hoverLayers[dir].addLayer(layer, label);
    },
    hoverEvent:function(layer, dir, key) {
        this.hoverLayers[dir].update(layer, key);
    },
    turnOn:function(dir) {
        this.turnOff();
        this.map.addLayer(this.layers[dir]);
        this.activeDir = dir;
        this.map.fitBounds(this.namedLayers[dir]['route'].getBounds());
    },
    turnOff:function() {
        if(this.activeDir != null) {
            this.map.removeLayer(this.layers[this.activeDir]);
            this.hoverLayers[this.activeDir].turnoff();
            this.activeDir = null;
        }
    }
};

function BuildTads(MAP_THIS) {
    this.MAP_THIS = MAP_THIS;
}

BuildTads.prototype = {
    style:styles.tadDefault,
    mouseover:function() {
        var MAP_THIS = this.MAP_THIS;
        return function(e) {
            var layer = e.target;
            var dir = layer.feature.properties.dir;
            var tad = layer.feature.properties.tad;
            MAP_THIS.dirLayers.hoverEvent(layer, dir, tad);
        }
    },
    build:function(data) {
        //console.log(this.THIS);
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
    buildLabels:function(summary, offs, geoms) {
        var THIS = this;
        var features = {};
        //var id = 1;
        $(summary).each(function(index, on_tad) {
            var labels = new L.featureGroup();
            $(offs[on_tad.tad].offs).each(function(index, off_tad) {
                if(geoms.hasOwnProperty(off_tad.tad)) {
                    var pct = off_tad.offs / on_tad.ons;
                    var centroid = geoms[off_tad.tad].centroid;
                    var pct_label = Math.round(pct * 100) + '%';
                    /*
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
                    var labelIcon = L.divIcon({
                        iconSize:[diameter, diameter],
                        html:svg.outerHTML,
                        className:''
                    });
                    */ 
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

function Map(mapDiv, url) {
    this.map = initmap(mapDiv);
    this.dirLayers = new DirectionLayers(this.map);
    this.hoverLayers = new HoverLayers(this.map);
    this.url = url;
}

Map.prototype = {
    activateRoute:function(args, statusCog) {
        var THIS = this;
        
        $(statusCog).show();

        $.getJSON(this.url, args, function(data) {
            THIS.dirLayers.reset();
            THIS.buildData(data);
            THIS.dirLayers.turnOn(1);
            $(statusCog).hide();
        });
    },
    buildData:function(data) {
        var THIS = this;
        var tads = new BuildTads(THIS);
        var routes = new BuildRoutes(THIS);
        var offs = new BuildOffs(THIS);
        var tadLayers = tads.build(data.tads);
        var routeLayers = routes.build(data.routes, data.minmax);
        $([0, 1]).each(function(index, dir) {
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
            THIS.dirLayers.addHoverLayer(dir, offLayer, 'offs');
            THIS.dirLayers.addHoverLayer(dir, offLabelLayer, 'labels');
            THIS.dirLayers.addLayer(dir, tadLayers[dir], 'tad');
            THIS.dirLayers.addLayer(dir, routeLayers[dir].route, 'route');
            THIS.dirLayers.addLayer(dir, routeLayers[dir].start, 'start');
            THIS.dirLayers.addLayer(dir, routeLayers[dir].end, 'end');
        });
        //$(offs.pies).each(function(index, pieID) {
        //    var pie = new d3pie(pieID, pieOptions);
        //});
        //console.log(offs);
    },
    activateDir:function(dir) {
        this.dirLayers.turnOn(dir); 
    }
}

