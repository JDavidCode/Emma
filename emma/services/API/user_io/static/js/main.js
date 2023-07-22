document.addEventListener('DOMContentLoaded', function () {
	var input = document.getElementById('commandInput');
	var sendBtn = document.getElementById('sendBtn');
	var textResponse = document.getElementById('response');

	sendBtn.addEventListener('click', function () {
		let message = input.value;
		socket.emit('message', message);
		input.value = ''; // Clear the input field after sending
	});

	function getQueryParams(url) {
		var queryParams = {};
		var query = url.split('?')[1];
		if (query) {
			query.split('&').forEach(function (param) {
				var parts = param.split('=');
				if (parts.length >= 2) {
					queryParams[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1]);
				}
			});
		}
		return queryParams;
	}

	var socket = io.connect('', {
		query: getQueryParams(window.location.search) // Extract query parameters from the URL
	});

	// initialize socket.io
	socket.on('connect', function (data) {
		console.log("Connected!");
	});

	socket.on('error', function () {
		console.log("Error!");
	});

	// update the server data when new data arrives
	socket.on('response', function (data) {
		textResponse.textContent = data;
		synthesize(data);
	});

	function synthesize(text) {
		const menssage = new SpeechSynthesisUtterance(text);
		window.speechSynthesis.speak(menssage);
	}
});
