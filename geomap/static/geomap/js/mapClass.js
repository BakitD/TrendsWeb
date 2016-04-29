'use strict';

class MapDrawer {
    // Constructor
    constructor(mapId, mapConfig, authUserFlag) {
	this.map = null;
	this.woeids = [];
	this.layers = {};
	this.drawingFunction = null;
	this.mapConfig = mapConfig;
	this.drawFunction = null;

	var mapboxTiles = L.tileLayer(mapConfig.mapURL + mapConfig.accessToken, 
			{ attribution: mapConfig.attribution }
	);

	this.map = L.map(document.getElementById(mapId), {
				minZoom:mapConfig.minZoom, 
				maxZoom:mapConfig.maxZoom,
				zoomControl: false, 
				worldCopyJump: true,
				closePopupOnClick: false 
			}
		)
		.addLayer(mapboxTiles)
		.setView([mapConfig.initLat, mapConfig.initLng], mapConfig.initZoom);

	new L.Control.Zoom({ position: 'bottomright' }).addTo(this.map);

	// Setting type of draw function
	if (mapConfig.placing == 'circle') {
		this.drawFunction = this.drawCircle;
	}
	else {
		this.drawFunction = this.drawSquare;
	}

	// Setting callback's
	if (authUserFlag) {
		this.map.on('zoomend', function (e) {
			if (mapConfig.scales.indexOf(this.getZoom()) >= 0) {
				this.map.actionCallback();
			}
		});
		this.map.on('dragend', function (e) {
			if (mapConfig.scales.indexOf() >= 0) {
				this.map.actionCallback();
			}
		});
	}

    } //end of constructor

} // end of class definition



MapDrawer.prototype.actionCallback = function () {
	var bounds = this.map.getBounds()
	$.ajax({
		url : this.mapConfig.ajaxOnZoomUrl,
		type: 'POST',
		data: {
			southWestLatitude: parseFloat(bounds._southWest.lat),
			southWestLongitude: parseFloat(bounds._southWest.lng),
			northEastLatitude: parseFloat(bounds._northEast.lat),
			northEastLongitude: parseFloat(bounds._northEast.lng),
			scale: this.map.getZoom()
		},

		success : function(json) {
			var parsedJson = JSON.parse(json);
			if (parsedJson.trends) {
				this.drawOnMap(jd.trends);
			}		
		}
	});
}




MapDrawer.prototype.drawOnMap = function (trends) {
	items = this.drawFunction(trends);
	items.forEach(function(item) {
		var popup = new L.popup({closeOnClick:false, maxWidth:120,closeButton:false})
			.setLatLng([item.x, item.y])
			.setContent(item.content)
			.addTo(this.map);
	});
}


MapDrawer.prototype.drawCircle = function (trends) {
	var result = [];
	var keys = Object.keys(trends);
	keys.forEach(function(key){
		if(trends[key].trends.length > 0) {
			  var phi = 0.0;
			  var delta = 360.0 / trends[key].trends.length;
			  var radx = 0.055;
			  var rady = 0.08;				
			  trends[key].trends.forEach(function(trend) {
				var x = radx * Math.cos(phi) + parseFloat(trends[key].coordinates.latitude);
				var y = rady * Math.sin(phi) + parseFloat(trends[key].coordinates.longitude);
				phi = phi + delta;
				result.push( {'latitude' : x, 'longitude' : y, 'content' : trend });
			  });
		};
 	});
	return result;
}


MapDrawer.prototype.drawSquare = function (trends) {
	var result = [];
	var keys = Object.keys(trends);
	keys.forEach(function(key){
		if(trends[key].trends.length > 0) {
			  var latDelta = 0.08;
			  var lngDelta = 0.03;
			  var colums = parseInt(Math.sqrt(trends[key].trends.length));
			  var i = 0;
			  var x = parseFloat(trends[key].coordinates.latitude);
			  var y = parseFloat(trends[key].coordinates.longitude);
			  trends[key].trends.forEach(function(trend) {
				result.push( {'latitude' : x, 'longitude' : y, 'content' : trend });
				if(i > colums) {
					y += latDelta;
					x = parseFloat(trends[key].coordinates.latitude);
					i = 0;
				};
				i++;
				x += lngDelta;
			  });
		};
 	});
	return result;
}

//var mapDrawwer = new MapDrawer(mapId, mapConfig, authUserFlag);



