function initialDataCircle(map, trends) {
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
				map.addLayer(popup);
			  });
		};
 	});
}


function initialDataSquare(map, trends) {
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
				map.addLayer(popup);
				//popup.addTo(map);
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
}


function onZoom_callback(map, zoomValue) {
	var bounds = map.getBounds()
	$.ajax({
		url : '/ajax/map/zoom/',
		type: 'POST',
		data: {
			southWestLatitude: parseFloat(bounds._southWest.lat),
			southWestLongitude: parseFloat(bounds._southWest.lng),
			northEastLatitude: parseFloat(bounds._northEast.lat),
			northEastLongitude: parseFloat(bounds._northEast.lng),
			zoomValue: zoomValue
		},

		success : function(json) {
			var jd = JSON.parse(json);
			 //&& Object.keys(jd.trends).length > 0
			if (jd.trends) {
				initialDataSquare(map, jd.trends);
			}		
		}		
	});
}


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

	// Load initial data
	if (mapConfig.placing == 'circle') {
		initialDataCircle(map, trends);
	}
	else {
		initialDataSquare(map, trends);
	}

	// On map zoon callback function
	if (authUserFlag) {
		//var old_zoom_value = map.getZoom();
		map.on('zoomend', function (e) {
			//var new_zoom_value = map.getZoom();
			//if (new_zoom_value > old_zoom_value) {
			scale = map.getZoom();
			if (mapConfig.scales.indexOf(scale) >= 0) {
				onZoom_callback(map, scale);
				console.log(scale);
			}
			//old_zoom_value = new_zoom_value;
		});
	}

} // renderMap function




