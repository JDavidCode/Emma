document.addEventListener('DOMContentLoaded', function () {
	const input = document.getElementById('commandInput');
	const sendBtn = document.getElementById('sendBtn');
	const chat = document.getElementById('chat');

	sendBtn.addEventListener('click', function () {
		let message = input.value;
		processChat(message)

	});

	function handleKeyDown(event) {
		// Check if the pressed key is the Enter key (keyCode 13)
		if (event.keyCode === 13) {
			event.preventDefault(); // Prevent the default behavior (new line in textarea)

			// Call your desired function here
			let message = input.value;
			processChat(message)
		}
	}
	function processChat(message) {
		const listItem = document.createElement('li');
		listItem.textContent = message;
		chat.appendChild(listItem);
		socket.emit('message', message);
		input.value = '';
	}
	input.addEventListener("keydown", handleKeyDown);

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

	socket.on('response', function (data) {
		// Obtener el elemento de la lista

		// Crear un nuevo elemento de lista (<li>) para mostrar la respuesta
		const listItem = document.createElement('li');
		listItem.textContent = data;

		// Agregar el nuevo elemento de lista a la lista existente
		chat.appendChild(listItem);

		// Llamar a la función synthesize (supongo que esta función reproduce el texto en voz)
		synthesize(data);
	});

	function synthesize(text) {
		const menssage = new SpeechSynthesisUtterance(text);
		window.speechSynthesis.speak(menssage);
	}
});
