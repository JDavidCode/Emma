document.addEventListener('DOMContentLoaded', function () {

	const socket = io.connect('', {
		query: getQueryParams(window.location.search) // Extract query parameters from the URL
	});

	///CONFIG
	const configBtn = document.getElementById('config-btn');
	const configContainer = document.getElementById('config-container');
	const closeConfigBtn = document.getElementById('close-config-btn')
	///Themes
	const darkModeToggle = document.getElementById('dark-mode-toggle');
	const darkModeToggler = document.getElementById('dark-mode-toggler');

	///TOOLKITS
	const createGroupBtn = document.getElementById("create-new-group-btn");
	const createGroupSubmitBtn = document.getElementById("create-group-submit-btn");
	const createGroupContainer = document.getElementById("new-group-container");
	const createChatBtn = document.getElementById('create-new-chat-btn');
	const createChatContainer = document.getElementById('new-chat-container');
	const createChatSubmitBtn = document.getElementById('create-chat-submit-btn');

	///CHAT
	const chatBox = document.getElementById("chat-content-box")

	///CHAT INPUTS
	const attachDocs = document.getElementById("attach-docs");
	const messageInput = document.getElementById("message-input");
	const messageSend = document.getElementById("message-send");
	const speakBtn = document.getElementById('message-speak');

	const favoriteBtns = document.querySelectorAll(".favorite-btn");
	let currentUtterance;

	darkModeToggle.addEventListener('click', () => {
		const currentValue = darkModeToggler.value;
		if (currentValue === '1') {
			darkModeToggler.value = '0'
			document.body.classList.toggle('dark-mode');
		} else {
			darkModeToggler.value = '1'
			document.body.classList.toggle('dark-mode');

		}
	});

	configBtn.addEventListener('click', () => {
		configContainer.style.display = 'block'
	})
	closeConfigBtn.addEventListener('click', () => {
		configContainer.style.display = 'none'
	})

	messageSend.addEventListener('click', function () {
		let message = messageInput.value;
		if (message !== "") {
			socket.emit('message', message);
			processChat(message, 'user-message');
		}
	});

	speakBtn.addEventListener('click', function () {
		// Stop the ongoing speech synthesis, if any
		stopSpeechSynthesis();
		startSpeechRecognition();
	});

	createGroupBtn.addEventListener("click", function () {
		createGroupContainer.style.display = createGroupContainer.style.display === "block" ? "none" : "block";
	});

	createGroupSubmitBtn.addEventListener("click", () => {
		const groupName = document.getElementById("group-name").value;
		if (groupName) {
			const newGroupItem = document.createElement("option");
			newGroupItem.value = groupName.toLowerCase().replace(/\s/g, "");
			newGroupItem.innerText = groupName;
			const groupList = document.getElementById("group-list");
			groupList.appendChild(newGroupItem);
			createGroupContainer.style.display = "none";
		} else {
			alert("Please enter a group name");
		}
	});

	createChatBtn.addEventListener('click', function () {
		createChatContainer.style.display = createChatContainer.style.display === "block" ? "none" : "block";
	});

	createChatSubmitBtn.addEventListener('click', function () {
		createChatContainer.style.display = 'none';
	});

	attachDocs.addEventListener("click", () => {
		const input = document.createElement("input");
		input.type = "file";
		input.onchange = (event) => {
			const file = event.target.files[0];
			const fileName = file.name;
			console.log("Attaching document: " + fileName);
		};
		input.click();
	});


	favoriteBtns.forEach((btn) => {
		btn.addEventListener("click", () => {
			console.log("Favorite button clicked");
		});
	});
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
		const listItem = document.createElement('p');
		listItem.textContent = message;
		listItem.classList.add("message", messageClass);// Add message class to the list item
		chatBox.appendChild(listItem);
		messageInput.value = '';
		scrollToBottom();

	}

	socket.on("load session", function (data) {
		chatContent(data);
	});

	socket.on('response', function (data) {
		if (isLink(data)) {
			// If it's a link, open it in a new tab/window
			window.open(data, '_blank');
		} else {
			processChat(data, 'emma-message');

			if (data.chat_content && data.chat_content.length > 0) {
				loadChatHistory(data.chat_content);
			}

			currentUtterance = new SpeechSynthesisUtterance(data);
			window.speechSynthesis.speak(currentUtterance);
		}
	});


	function createCard(type, title, description, imageUrl) {
		// Crear elementos
		var card = document.createElement("div");
		card.className = "row mx-auto my-1 col-11 " + type + "-card";

		var innerRow1 = document.createElement("div");
		innerRow1.className = "row my-2";

		var imageCol = document.createElement("div");
		imageCol.className = "col-2 p-0 my-auto ml-1";

		var image = document.createElement("img");
		image.className = "round_image";
		image.src = imageUrl;

		var innerRow2 = document.createElement("div");
		innerRow2.className = "row col-10 p-0 ml-1";

		var cardInfoCol = document.createElement("div");
		cardInfoCol.className = "col-8 card-info m-0 p-0";

		var cardTitle = document.createElement("p");
		cardTitle.className = "card-title my-1";
		cardTitle.textContent = title;

		var cardDescription = document.createElement("p");
		cardDescription.className = "card-description my-0";
		cardDescription.textContent = description;

		var cardControlsCol = document.createElement("div");
		cardControlsCol.className = "col-2 card-controls d-flex p-0 m-0 ml-3 align-items-center";

		var heartButton = document.createElement("button");
		var heartIcon = document.createElement("i");
		heartIcon.className = "ti-heart";
		heartButton.appendChild(heartIcon);

		var moreButton = document.createElement("button");
		var moreIcon = document.createElement("i");
		moreIcon.className = "ti-more";
		moreButton.appendChild(moreIcon);

		// Anidar elementos
		imageCol.appendChild(image);
		cardInfoCol.appendChild(cardTitle);
		cardInfoCol.appendChild(cardDescription);
		cardControlsCol.appendChild(heartButton);
		cardControlsCol.appendChild(moreButton);
		innerRow2.appendChild(cardInfoCol);
		innerRow2.appendChild(cardControlsCol);
		innerRow1.appendChild(imageCol);
		innerRow1.appendChild(innerRow2);
		card.appendChild(innerRow1);

		// Agregar a la página
		return card
	}

	function isLink(text) {
		// Regular expression to match common URL patterns
		const urlPattern = /(http|https):\/\/[^\s]+/;

		// Decode the URL before checking using the regular expression
		const decodedText = decodeURIComponent(text);

		// Check if the decoded response contains a link using the regular expression
		return urlPattern.test(decodedText);
	}

	function chatContent(data) {
		// Agregar mensajes del historial al DOM
		data.chat_content.forEach(message => {
			// Verificar si el mensaje ya está presente en el chat para evitar duplicados
			if (!isMessagePresent(chatBox, message.content)) {
				const listItem = document.createElement('p');
				listItem.textContent = message.content;
				listItem.classList.add("message", message.role === 'user' ? 'user-message' : 'emma-message');
				chatBox.appendChild(listItem);
			}
		});
		scrollToBottom();
	}

	function isMessagePresent(chat, messageContent) {
		// Verificar si el mensaje ya está presente en el chat
		const existingMessages = chat.querySelectorAll('.message');
		for (const existingMessage of existingMessages) {
			if (existingMessage.textContent === messageContent) {
				return true;
			}
		}
		return false;
	}
	socket.on('update chat', function (data) {
		processChat(data, 'user-message')
	});




	function verifyInputState() {
		let value = messageInput.value
		if (value === '') {
			speakBtn.style.display = 'block'
			messageSend.style.display = 'none'

		} else {
			speakBtn.style.display = 'none'
			messageSend.style.display = 'block'
		}
	}
	verifyInputState();
	setInterval(verifyInputState, 500);

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

	function scrollToBottom() {
		chatBox.scrollTop = chatBox.scrollHeight;
	}

	function handleKeyDown(event) {
		if (event.keyCode === 13) {
			event.preventDefault();
			let message = messageInput.value;
			if (message !== "") {
				socket.emit('message', message);
				processChat(message, 'user-message');
			}// Assign user message class
		}
	}
	messageInput.addEventListener("keydown", handleKeyDown);
})