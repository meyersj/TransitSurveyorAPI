function EventHandler(map, defaultStyle, eventStyle) {
    this.map = map;
    this.eventKey = null;
    this.eventFeature = null;
    this.displayLayers = {};
    this.defaultStyle = defaultStyle;
    this.eventStyle = eventStyle;
}

EventHandler.prototype.clear = function() {
    if(this.eventFeature) {
        if(this.displayLayers.hasOwnProperty(this.eventKey)) {
            this.map.removeLayer(this.displayLayers[this.eventKey]);
        }
        this.eventFeature.setStyle(this.defaultStyle);
    }
    this.eventKey = null;
    this.eventFeature = null;
}

EventHandler.prototype.activate = function(feature, key) {
    console.log(feature);
    console.log(key);
    if(this.eventKey == key) return false;
    if(this.eventFeature) {
        if(this.displayLayers.hasOwnProperty(this.eventKey)) {
            this.map.removeLayer(this.displayLayers[this.eventKey]);
        }
        this.eventFeature.setStyle(this.defaultStyle);
    }
    feature.setStyle(this.eventStyle);
    if(this.displayLayers.hasOwnProperty(key)) {
        this.map.addLayer(this.displayLayers[key]);
    }
    this.eventKey = key;
    this.eventFeature = feature;
    return true;
}

EventHandler.prototype.addLayer = function(layer, key) {
    if(!this.displayLayers.hasOwnProperty(key)) {
        this.displayLayers[key] = L.featureGroup();
    }
    this.displayLayers[key].addLayer(layer);
}


function View(map, args) {
    this.map = map;
    this.rte = args.rte;
    this.dir = args.dir;
    this.viewName = args.viewName;
    this.displayLayers = L.featureGroup();
    this.eventHandler = new EventHandler(this.map, args.defaultStyle, args.eventStyle);
}

View.prototype.triggerEvent = function(feature, key) {
    return this.eventHandler.activate(feature, key);
}

View.prototype.addEventLayer = function(layer, key) {
    if(layer instanceof L.Class) {
        this.eventHandler.addLayer(layer, key);
        return true;
    }
    return false;
}

View.prototype.addDisplayLayer = function(layer) {
    if(layer instanceof L.Class) {
        this.displayLayers.addLayer(layer);
        return true;
    }
    return false;
}


View.prototype.turnOn = function() {
    this.map.addLayer(this.displayLayers);
    this.map.fitBounds(this.displayLayers.getBounds());
    return true;
}

View.prototype.turnOff = function() {
    this.map.removeLayer(this.displayLayers);
    this.eventHandler.clear();
    return true;
}


function ViewManager() {
    this.routes = [];
    this.curView = null;
    this.curRte = null;
    this.curDir = null;
    this.curViewName = null;
    this.views = {};
}

ViewManager.prototype.addRoute = function(rte) {
    this.routes.push(rte);
}

ViewManager.prototype.routeDownloaded = function(rte) {
    var THIS = this;
    var retVal = false;
    $(THIS.routes).each(function(index, route) {
        if(rte == route) retVal = true;
    });
    return retVal;
}

ViewManager.prototype.createViewID = function(rte, dir, viewName) {
    return rte + '|' + dir + '|' + viewName;
}

ViewManager.prototype.getViewID = function(view) {
    if(!view instanceof View) return '';
    return view.rte + '|' + view.dir + '|' + view.viewName;
}


ViewManager.prototype.addView = function(view) {
    if(!view instanceof View) return false;
    var viewID = this.getViewID(view);
    this.views[viewID] = view;
    return true;
}

ViewManager.prototype.turnOn = function() {
    if(this.curView != null) {
        this.curView.turnOn();
        return true;
    }
    return false;
}

ViewManager.prototype.turnOff = function() {
    if(this.curView) {
        console.log(this.curView);
        this.curView.turnOff()
        this.curView = null;
        return true;
    }
    return false;
}

ViewManager.prototype.activateView = function(rte, dir, viewName) {
    var id = this.createViewID(rte, dir, viewName);
    var view = this.views[id];
    if(this.curView == view) return false;
    if(view) {
        this.turnOff();
        this.curRte = rte;
        this.curDir = dir;
        this.curViewNam = viewName;
        this.curView = view;
        this.turnOn();
        return true;
    }
    else {
        this.turnOff();
        this.curView = null;
        return false;
    }
}

