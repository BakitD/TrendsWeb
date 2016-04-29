woeids = [];

function addWoeid(woeid) {
	if (woeids.indexOf(woeid) < 0) {
		woeids.push(woeid);
	}
}

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
				addWoeid(key);
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
				addWoeid(key);
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


function drawOnMap(map, items) {
	items.forEach(function(item) {
		item.addTo(map);
	});
	console.log(woeids);
	//L.layerGroup(items).addTo(map);
}


// Callback function on map zooming.
// Requests places for coordinates that is inside
// bounds. Return list of popups.
function onZoom_callback(map, url, drawFunction) {
	var bounds = map.getBounds()
	$.ajax({
		url : url,
		type: 'POST',
		data: {
			southWestLatitude: parseFloat(bounds._southWest.lat),
			southWestLongitude: parseFloat(bounds._southWest.lng),
			northEastLatitude: parseFloat(bounds._northEast.lat),
			northEastLongitude: parseFloat(bounds._northEast.lng),
			scale: map.getZoom()
		},

		success : function(json) {
			var jd = JSON.parse(json);
			if (jd.trends) {
				popups = drawFunction(jd.trends);
				drawOnMap(map, popups);
			}		
		}
	});
}

// Initialization function.
function renderMap(mapId, trends, mapConfig, authUserFlag) {

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
	drawFunction = initialDataSquare;
	if (mapConfig.placing == 'circle') {
		drawFunction = initialDataCircle;
	}

	// Defining layer groups dictionary
	var layers = {};

	// Load initial data if initScaleIndex exists
	if ('initScaleIndex' in mapConfig) {
		layers[mapConfig.initScaleIndex] = drawFunction(trends);
		drawOnMap(map, layers[mapConfig.initScaleIndex]);
	}

	// On map zoon callback function
	if (authUserFlag) {
		map.on('zoomend', function (e) {
			scale = map.getZoom();
			if (mapConfig.scales.indexOf(scale) >= 0) {
				console.log(scale);
				onZoom_callback(map, mapConfig.ajaxOnZoomUrl, drawFunction);
			}
		});
		map.on('dragend', function (e) {
			scale = map.getZoom();
			if (mapConfig.scales.indexOf(scale) >= 0) {
				onZoom_callback(map, mapConfig.ajaxOnZoomUrl, drawFunction);
			}
		});
	}

}



