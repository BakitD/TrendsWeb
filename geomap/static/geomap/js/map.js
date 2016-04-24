function rand() {
	return 0;parseFloat((Math.random() * (0.005 + 0.005) - 0.005).toFixed(8));
}


function initialData(map, trends) {
	var keys = Object.keys(trends);
	keys.forEach(function(key){
		if(trends[key].trends.length > 0) {
			  var phi = 0.0;
			  var delta = 360.0 / trends[key].trends.length;
			  var radx = 0.03;
			  var rady = 0.06;				
			  trends[key].trends.forEach(function(trend) {
				var x = radx * Math.cos(phi) + parseFloat(trends[key].coordinates.latitude);
				var y = rady * Math.sin(phi) + parseFloat(trends[key].coordinates.longitude);
				phi = phi + delta;
				var popup = new L.popup({closeOnClick:false})
					.setLatLng([x, y])
					.setContent(trend);
				map.addLayer(popup);
			  });
		};
 	}); // keys.forEach
} // initialData


function onMapZoom(map) {
	/*var currentZoom = map.getZoom();
	switch (currentZoom) {
		case 4:
			console.log(currentZoom);
			break;
		case 7:
			console.log(currentZoom);
			break;
		case 14:
			console.log('Stop zooming me!');
			break;
		default:
			break;
	}*/
	var bounds = map.getBounds()
	$.ajax({
		url : '/ajax/map/zoom/',
		type: 'POST',
		data: {
			southWestLatitude: bounds._southWest.lat,
			southWestLongitude: bounds._southWest.lng,
			northEastLatitude: bounds._northEast.lat,
			northEastLongitude: bounds._northEast.lng
		},

		success : function(json) {
			console.log(json);
		}

		
	});

}



function renderMap(mapId, trends, mapConfig) {

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
	initialData(map, trends);

	// On map zoon callback function
	map.on('zoomend', function (e) {
	    onMapZoom(map);
	});

} // renderMap function




