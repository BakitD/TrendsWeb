google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);
google.load('visualization', '1.0', {'packages':['corechart']});


function drawChart(tendency) {
	var matrix = [];
	var ptimes = tendency.time;
	ptimes.forEach(function(item, i, ptimes) {
		var time = new Date(item);
		var day = time.getUTCDate();
		var month = time.getUTCMonth();
		var year = time.getUTCFullYear();
		matrix.push([day + '/' + month + '/' + year, tendency.volume[i]]);
	});
	matrix.unshift(['Datetime', ''])
	var data = google.visualization.arrayToDataTable(matrix);


	var options = {
		legend: {position: 'none'},
		title: 'График популярности темы',
		width: 850,
		height: 400,
		curveType: 'function',
		backgroundColor : 'transparent',
		hAxis: { textPosition: 'none' },
          	vAxis: {title: 'Количество упоминаний', gridlines: {color:'grey'}},
		series: {0:{color:'FF6900',lineWidth:2}}
	};

	var chart = new google.visualization.LineChart(document.getElementById('chartGraph'));
	chart.draw(data, options);
}
