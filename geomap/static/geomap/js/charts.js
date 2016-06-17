google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);
google.load('visualization', '1.0', {'packages':['corechart']});

var HAXIS_LABELS_NUMBER = 5;
var TICKS_COUNT = 0;

function drawChart(tendency) {
	var matrix = [];
	var ticks_v = [];
	var ptimes = tendency.time;
	/*if ( typeof ptimes != 'undefined' ) {
		TICKS_COUNT = ptimes.length / HAXIS_LABELS_NUMBER;
	};*/

	ptimes.forEach(function(item, i, ptimes) {
		var time = new Date(item);
		var day = time.getDate();
		var month = time.getMonth();
		var year = time.getFullYear();
		matrix.push([day + '/' + (month+1) + '/' + year, tendency.volume[i]]);
	});

	matrix.unshift(['Datetime', ''])
	var data = google.visualization.arrayToDataTable(matrix);

	var options = {
		legend: {position: 'none'},
		title: 'График популярности темы',
		width: 850,
		height: 400,
		curveType: 'function',
		pointSize: 2,
		backgroundColor : 'transparent',
		//hAxis: {title: 'Дата', textPosition: 'none'},
		hAxis: { textPosition: 'none', },
		//hAxis: {ticks: ticks_v},},
		//hAxis: {gridlines: {color:'grey', count:  HAXIS_LABELS_NUMBER}, showTextEvery: TICKS_COUNT},
          	vAxis: {title: 'Количество упоминаний', gridlines: {color:'grey'}, },
		series: {0:{color:'FF6900',lineWidth:2}}
	};

	var chart = new google.visualization.LineChart(document.getElementById('chartGraph'));
	chart.draw(data, options);
}
