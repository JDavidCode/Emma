document.addEventListener('DOMContentLoaded', function () {
	var input = document.getElementById('commandInput');
	var sendBtn = document.getElementById('sendBtn');
	var textResponse = document.getElementById('response');

	sendBtn.addEventListener('click', function () {
		let message = input.value;
		socket.emit('message', message);
		input.value = ''; // Clear the input field after sending
	});

	var socket = io.connect();

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
		console.log(data);
	});
});
