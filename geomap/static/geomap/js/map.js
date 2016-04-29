// Function creates popups array with coordinates
// that makes popups located around central point.
function initialDataCircle(trends) {
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
				var popup = new L.popup({closeOnClick:false, maxWidth:120, closeButton:false})
					.setLatLng([x, y])
					.setContent(trend);
				result.push(popup);
			  });
		};
 	});
	return result;
}

// Function creates popups array with coordinates
// that makes popups located as table.
function initialDataSquare(trends) {
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
				var popup = new L.popup({closeOnClick:false, maxWidth:120,closeButton:false})
					.setLatLng([x, y])
					.setContent(trend);
				result.push(popup);
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

// TODO Continue gere Layers
// use clearLayers();
layers = {};

function drawOnMap(map, items, scale) {
	if (layers[scale] != undefined) {
		layers[scale].addLayer(L.layerGroup(items));
	}
	else {
		layers[scale] = L.layerGroup(items);
	}
	layers[scale].addTo(map);
}


// Callback function on zoomend and dragend.
// Requests places for coordinates that's inside the bounds.
function onMapAction(map, url, drawFunction, scale) {
	var bounds = map.getBounds()
	if (scale == undefined) {
		scale = map.getZoom();
	}
	$.ajax({
		url : url,
		type: 'POST',
		data: {
			southWestLatitude: parseFloat(bounds._southWest.lat),
			southWestLongitude: parseFloat(bounds._southWest.lng),
			northEastLatitude: parseFloat(bounds._northEast.lat),
			northEastLongitude: parseFloat(bounds._northEast.lng),
			scale: scale
		},

		success : function(json) {
			var jd = JSON.parse(json);
			if (jd.trends) {
				drawOnMap(map, drawFunction(jd.trends), scale);
			}
		}
	});
}

// Initialization function.
function renderMap(mapId, mapConfig, authUserFlag) {

	// Initializing map
	L.mapbox.accessToken = mapConfig.accessToken;
	var mapLayerURL = mapConfig.mapURL + L.mapbox.accessToken
	var mapboxTiles = L.tileLayer(mapLayerURL, {attribution: mapConfig.attribution });

	var map = L.map(document.getElementById(mapId), {
				minZoom:mapConfig.minZoom, 
				maxZoom:mapConfig.maxZoom,
				zoomControl: false, 
				worldCopyJump: true,
				closePopupOnClick: false 
			}
		)
		.addLayer(mapboxTiles)
		.setView([mapConfig.initLat, mapConfig.initLng], mapConfig.initZoom);

	new L.Control.Zoom({ position: 'bottomright' }).addTo(map);

	// Set drawing function
	drawFunction = (mapConfig.placing == 'square') ? initialDataSquare : initialDataCircle;


	// Call function for initial trends
	onMapAction(map, mapConfig.ajaxOnZoomUrl, drawFunction, mapConfig.initScaleIndex);


	// On map zoon callback function
	if (authUserFlag) {
		map.on('zoomend', function (e) {
			if (mapConfig.scales.indexOf(map.getZoom()) >= 0) {
				onMapAction(map, mapConfig.ajaxOnZoomUrl, drawFunction);
			}
		});
		map.on('dragend', function (e) {
			if (mapConfig.scales.indexOf(map.getZoom()) >= 0) {
				onMapAction(map, mapConfig.ajaxOnZoomUrl, drawFunction);
			}
		});
	}

}


