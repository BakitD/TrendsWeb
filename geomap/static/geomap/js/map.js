function rand() {
	return parseFloat((Math.random() * (0.02 + 0.02) - 0.02).toFixed(8));
};

function renderMap(mapId, trends) {
	L.mapbox.accessToken = 'pk.eyJ1IjoiYmFraXQiLCJhIjoiY2ltZHMzbWNiMDAyOHdka2toYzdkNTc4ciJ9.5nYeNUZPv2ohnoYWknNIpw';

	var mapboxTiles = L.tileLayer('https://api.mapbox.com/v4/bakit.dc14b0c3/'+
		'{z}/{x}/{y}.png?access_token=' + L.mapbox.accessToken, {
		attribution: '© <a href="https://www.mapbox.com/map-feedback/'+
		'">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'});

	var map = L.map(document.getElementById(mapId), { zoomControl: false, closePopupOnClick : false })
		.addLayer(mapboxTiles)
		.setView([40,2], 3);

	new L.Control.Zoom({ position: 'bottomright' }).addTo(map);
	var keys = Object.keys(trends);

	keys.forEach(function(key){
		if(trends[key].trends.length > 0) {
		  var phi = 0.0;
		  var delta = 360.0 / trends[key].trends.length;
		  var radx = 0.02;
		  var rady = 0.04;				
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
	});
};
