
function splitData(rawData) {
	var categoryData = [];
	var kline = [];
	var force_raw = [];
	var force_ema = [];
	var model_signal = [];

	for (var i = 0; i < rawData.length; i++) {
		var date = rawData[i][0];
		var open = rawData[i][1];
		var close = rawData[i][2];
		var low = rawData[i][3];
		var high = rawData[i][4];
		var w_pulse = rawData[i][5];
		var w_pulse_signal = rawData[i][6];
		var enter_point = rawData[i][7];
		var target_point = rawData[i][8];
		var stop_point = rawData[i][9];
		var f_raw = rawData[i][10];
		var f_ema = rawData[i][11];
		var f_signal = rawData[i][12];
		var m_signal = rawData[i][13];

		categoryData.push(date);

		kline.push([i, open, close, low, high, w_pulse]);
		model_signal.push([i, close, m_signal]);
		force_raw.push([i, f_raw, f_ema, f_signal])
		force_ema.push([i, f_ema, f_signal])
	}
	return {
		categoryData: categoryData,
		kline: kline,
		model_signal: model_signal,
		force_raw: force_raw,
		force_ema: force_ema
	};
}

function renderItem(params, api) {
	var xValue = api.value(0);
	var openPoint = api.coord([xValue, api.value(1)]);
	var closePoint = api.coord([xValue, api.value(2)]);
	var lowPoint = api.coord([xValue, api.value(3)]);
	var highPoint = api.coord([xValue, api.value(4)]);
	var pulse_color = api.value(5);
	var halfWidth = api.size([1, 0])[0] * 0.35;
	var style = api.style({
		stroke: api.visual('color')
	});

	if(pulse_color == "r"){
		style.stroke = "#FF0000";
	}
	else if(pulse_color == "b"){
		style.stroke = "#0000FF";
	}
	else if(pulse_color == "g"){
		style.stroke = "#00FF00";
	}

	return {
		type: 'group',
		children: [{
			type: 'line',
			shape: {
				x1: lowPoint[0], y1: lowPoint[1],
				x2: highPoint[0], y2: highPoint[1]
			},
			style: style
		}, {
			type: 'line',
			shape: {
				x1: openPoint[0], y1: openPoint[1],
				x2: openPoint[0] - halfWidth, y2: openPoint[1]
			},
			style: style
		}, {
			type: 'line',
			shape: {
				x1: closePoint[0], y1: closePoint[1],
				x2: closePoint[0] + halfWidth, y2: closePoint[1]
			},
			style: style
		}]
	};
}


function renderModelSignal(params, api) {

	var pos = api.coord([api.value(0), api.value(1)]);
	var model_signal = api.value(2);

	//var style = api.style();
	var style = {};

	var invisible = false;
	
	style.text = model_signal;
	style.x = pos[0];
	style.y = pos[1];

	if(model_signal == 0){
		return;
	}
	else if(model_signal >= 4){
		//style.fill = "#00FF00";
	}
	else if(model_signal < 0){
		style.fill = "#FF0000";
	}

	return {
		type: 'text',
		invisible: true,
		style: style
	};
}


function renderForceSignal(params, api) {

	var pos = api.coord([api.value(0), api.value(1)]);
	var force_signal = api.value(2);

	var style = api.style({
		stroke: api.visual('color')
	});

	var r = 0;
	var invisible = false;

	if(force_signal == "0"){
		invisible = true;
	}
	else if(force_signal == "1"){
		style.stroke = "#00FF00";
		style.fill = "#00FF00";
		r = 3;
	}
	else if(force_signal == "-1"){
		style.stroke = "#FF0000";
		style.fill = "#FF0000";
		r = 3;
	}

	return {
			type: 'circle',
			invisible: invisible,
			shape: {
				cx: pos[0], cy: pos[1], r: r
			},
			style: style
	};
}

function show(myChart) {

	var day = splitData(day_data);

	myChart.setOption(option = {
		backgroundColor: '#eee',
		animation: false,

		legend: {
			bottom: 10,
			left: 'center',
			data: ['kline', 'model_signal', 'force_ema', 'force_signal']
		},

		tooltip: {
			trigger: 'axis',
			axisPointer: {
				type: 'cross'
			},
			backgroundColor: 'rgba(245, 245, 245, 0.8)',
			borderWidth: 1,
			borderColor: '#ccc',
			padding: 10,
			textStyle: {
				color: '#000'
			},
			position: function (pos, params, el, elRect, size) {
				var obj = {top: 10};
				obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
				return obj;
			},
			extraCssText: 'width: 170px'
		},

		axisPointer: {
			link: {xAxisIndex: 'all'},
			label: {
				backgroundColor: '#777'
			}
		},

		toolbox: {
			feature: {
				dataZoom: {
					yAxisIndex: false
				},
				brush: {
					type: ['lineX', 'clear']
				}
			}
		},

		brush: {
			xAxisIndex: 'all',
			brushLink: 'all',
			outOfBrush: {
				colorAlpha: 0.1
			}
		},
		
		grid: [
		{
			left: '10%',
			right: '8%',
			height: '50%'
		},
		{
			left: '10%',
			right: '8%',
			top: '70%',
			height: '16%'
		}
		],

		xAxis: [
		{
			type: 'category',
			data: day.categoryData,
			scale: true,
			boundaryGap : false,
			axisLine: {onZero: false},
			splitLine: {show: false},
			splitNumber: 20,
			min: 'dataMin',
			max: 'dataMax',
			axisPointer: {
				z: 100
			}
		},
		{
			type: 'category',
			gridIndex: 1,
			data: day.categoryData,
			scale: true,
			boundaryGap : false,
			axisLine: {onZero: false},
			splitLine: {show: false},
			splitNumber: 20,
			min: 'dataMin',
			max: 'dataMax',
			axisPointer: {
				z: 100
			}
		}
		],

		yAxis: [
		{
			scale: true,
			splitArea: {
				show: true
			}
		},
		{
			scale: true,
			gridIndex: 1,
			splitArea: {
				show: true
			}
		}
		],

		dataZoom: [
		{
			type: 'inside',
			xAxisIndex: [0, 1],
			start: 98,
			end: 100,
			minValueSpan: 10
		},
		{
			show: true,
			type: 'slider',
			xAxisIndex: [0, 1],
			bottom: 60,
			start: 98,
			end: 100,
			minValueSpan: 10
		}
		],

		series: [
		{
			name: 'kline',
			type: 'custom',
			renderItem: renderItem,
			dimensions: [null, 'open', 'close', 'lowest', 'highest'],
			encode: {
				x: 0,
				y: [1, 2, 3, 4],
				tooltip: [1, 2, 3, 4]
			},
			data: day.kline
		},

		{
			name: 'model_signal',
			type: 'custom',
			renderItem: renderModelSignal,
			dimensions: [null, 'close', 'model_signal'],
			encode: {
				x: 0,
				y: [1],
				tooltip: [1, 2]
			},
			data: day.model_signal
		},

		{
			name: 'force_ema',
			type: 'line',
			dimensions: [null, 'force_ema'],
			encode: {
				x: 0,
				y: [1],
				tooltip: [1]
			},
			markLine: {
				data: [
					{
						name: '',
						yAxis: 0
					}
				]
			},
			data: day.force_ema,
			xAxisIndex: 1,
			yAxisIndex: 1
		},
		{
			name: 'force_signal',
			type: 'custom',
			renderItem: renderForceSignal,
			dimensions: [null, 'force_ema', 'force_signal'],
			encode: {
				x: 0,
				y: [1],
				tooltip: [2]
			},
			data: day.force_ema,
			xAxisIndex: 1,
			yAxisIndex: 1
		},
		]
	}, true);

	//myChart.dispatchAction({
		//type: 'brush',
		//areas: [
		//{
			//brushType: 'lineX',
			//xAxisIndex: 0
		//}
		//]
	//});

}


