function initmap(map_div) {
    // set up the map
    var map = new L.Map(map_div);

    // create the tile layer with correct attribution
    var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    //osmUrl = 'https://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png';    
    var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
    var osm = new L.TileLayer(osmUrl, {
        minZoom: 8,
        maxZoom: 20,
        attribution: osmAttrib,
        id: 'examples.map-i86knfo3'
    });       

    // start the map in South-East England
    map.setView(new L.LatLng(45.51, -122.678),12);
    map.addLayer(osm);
    return map;
}

function makePieChart() {
      
     var quota = 200, count = 56;
      var data = [
          {label:'Remaining', value:quota-count},
          {label:'Complete', value:count}
      ];

      var svg = document.createElement('svg');
      nv.addGraph(function() {
          var chart = nv.models.pieChart()
              .x(function(d) { return d.label; })
              .y(function(d) { return d.value; })
              .showLegend(false)
              .showLabels(true);
   
          d3.select(svg)
              .attr('height', 200)
              .attr('width', 200)
              .datum(data)
              .transition().duration(250)
              .call(chart);
          
          return chart;
      });
      
      return svg;
}

