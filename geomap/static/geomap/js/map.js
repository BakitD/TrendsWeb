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

function clearMap(scale) {
	var keys = Object.keys(layers);
	keys.forEach(function(key) {
		if(key > scale && layers[key]) {
			layers[key].clearLayers();
		} 
	});
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

// Function is called on zoomend and dragend
function onZoomDrag(mapConfig, map, lastZoom, drawFunction) {
	var scale = map.getZoom();
	if (scale < lastZoom) {
		clearMap(scale);
	}
	if (mapConfig.scales.indexOf(scale) >= 0) {
		onMapAction(map, mapConfig.ajaxOnZoomUrl, drawFunction);
	}
	return scale;
}

// Initialization function.
function renderMap(mapId, mapConfig, authUserFlag, trends) {

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


	// On map zoon callback function
	var lastZoom = 0;
	if (authUserFlag) {
		onMapAction(map, mapConfig.ajaxOnZoomUrl, drawFunction, mapConfig.initScaleIndex);
		map.on('zoomend', function (e) {
			lastZoom = onZoomDrag(mapConfig, map, lastZoom, drawFunction);
		});
		map.on('dragend', function (e) {
			lastZoom = onZoomDrag(mapConfig, map, lastZoom, drawFunction);
		});
	}
	else {
		items = drawFunction(trends);
		drawOnMap(map, items, mapConfig.initScaleIndex);
	}
}


// Initialization function. Function for trend places tags.
function renderMapForTags(mapId, mapConfig, places) {

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

	for (key in places) {
		L.marker([parseFloat(places[key].latitude), 
			parseFloat(places[key].longitude)], 
			{'title':places[key].name}).addTo(map);
	};


}

