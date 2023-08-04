document.addEventListener('DOMContentLoaded', function () {
	const input = document.getElementById('commandInput');
	const sendBtn = document.getElementById('sendBtn');
	const speakBtn = document.getElementById('speakBtn'); // New speech recognition button
	const chat = document.getElementById('chat');
	let currentUtterance;

	function handleKeyDown(event) {
		if (event.keyCode === 13) {
			event.preventDefault();
			let message = input.value;
			socket.emit('message', message);

			processChat(message, 'user-message'); // Assign user message class
		}
	}
	input.addEventListener("keydown", handleKeyDown);

	sendBtn.addEventListener('click', function () {
		let message = input.value;
		socket.emit('message', message);
		processChat(message, 'user-message'); // Assign user message class
	});

	speakBtn.addEventListener('click', function () {
		// Stop the ongoing speech synthesis, if any
		stopSpeechSynthesis();
		startSpeechRecognition();
	});

	function isLink(text) {
		// Regular expression to match common URL patterns
		const urlPattern = /(http|https):\/\/[^\s]+/;

		// Decode the URL before checking using the regular expression
		const decodedText = decodeURIComponent(text);

		// Check if the decoded response contains a link using the regular expression
		return urlPattern.test(decodedText);
	}


	function startSpeechRecognition() {
		recognition = new webkitSpeechRecognition();
		recognition.lang = 'en-US';
		recognition.start();

		recognition.onresult = function (event) {
			const transcript = event.results[0][0].transcript;
			processChat(transcript, 'user-message');
			socket.emit('message', transcript);

		};

		recognition.onend = function () {
			console.log("Speech recognition ended.");
		};

		recognition.onerror = function (event) {
			console.error("Speech recognition error:", event.error);
		};
	}

	function stopSpeechSynthesis() {
		if (currentUtterance) {
			window.speechSynthesis.cancel(); // Stop the current speech synthesis
		}
	}

	function processChat(message, messageClass) {
		const listItem = document.createElement('li');
		listItem.textContent = message;
		listItem.classList.add("message", messageClass); // Add message class to the list item
		chat.appendChild(listItem);
		input.value = '';
	}

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

		if (isLink(data)) {
			// If it's a link, open it in a new tab/window
			window.open(data, '_blank');
		} else {
			processChat(data, 'emma-message');
			// If it's not a link, speak the message using speech synthesis
			currentUtterance = new SpeechSynthesisUtterance(data);
			window.speechSynthesis.speak(currentUtterance);
		}

	});

});
