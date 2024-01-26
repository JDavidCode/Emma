document.addEventListener('DOMContentLoaded', function () {

	const socket = io.connect('', {
		query: getQueryParams(window.location.search) // Extract query parameters from the URL
	});
	const currentDateTime = new Date();
	///CONFIG
	const configBtn = document.getElementById('config-btn');
	const configContainer = document.getElementById('config-container');
	const closeConfigBtn = document.getElementById('close-config-btn')
	const themeSelect = document.getElementById("theme-select");
	const voiceOption = document.getElementById("voice-toggle");
	const notificationOption = document.getElementById("notification-toggle")

	///TOOLKITS
	const toolkitsSelect = document.getElementById("toolkits");
	const createGroupSubmitBtn = document.getElementById("create-group-submit-btn");
	const createGroupContainer = document.getElementById("new-group-container");
	const createChatContainer = document.getElementById('new-chat-container');
	const createChatSubmitBtn = document.getElementById('create-chat-submit-btn');
	const closeChatContainerBtn = document.getElementById('close-new-chat-container-btn')
	const closeGroupContainerBtn = document.getElementById('close-new-group-container-btn')

	///CHAT
	const chatBox = document.getElementById("chat-content-box")

	///CHAT INPUTS
	const attachDocs = document.getElementById("attach-docs");
	const messageInput = document.getElementById("message-input");
	const messageSend = document.getElementById("message-send");
	const speakBtn = document.getElementById('message-speak');

	const favoriteBtns = document.querySelectorAll(".favorite-btn");
	let currentUtterance;


	themeSelect.addEventListener("change", event => {
		const selectedTheme = event.target.value;

		if (selectedTheme === "light") {
			document.body.classList.remove("dark-theme", "aqua-theme", "gray-scale-theme");
			document.body.classList.add("light-theme");
		} else if (selectedTheme === "dark") {
			document.body.classList.remove("light-theme", "aqua-theme", "gray-scale-theme");
			document.body.classList.add("dark-theme");
		} else if (selectedTheme === "custom") {
			// Add code here to handle custom theme
			applyCustomTheme();
		} else if (selectedTheme === "aqua") {
			document.body.classList.remove("light-theme", "dark-theme", "gray-scale-theme");
			document.body.classList.add("aqua-theme");
		} else if (selectedTheme === "gray") {
			document.body.classList.remove("light-theme", "dark-theme", "aqua-theme");
			document.body.classList.add("gray-scale-theme");
		}
	});


	notificationOption.addEventListener("change", function () {
		if (this.checked) {
			// Request permission to send notifications
			Notification.requestPermission()
				.then(permission => {
					// Check if the user granted permission
					if (permission === "granted") {
						// Create and show the notification
						const notification = new Notification("Hello, World!");
					} else {
						console.log("The user denied permission to send notifications.");
					}
				})
				.catch(error => {
					console.error("An error occurred while requesting permission:", error);
				});
		} else {
			// Cancel any pending notifications
			notification.close();
		}
	});

	configBtn.addEventListener('click', () => {
		configContainer.style.display = configContainer.style.display === "block" ? "none" : "block";
	})

	closeConfigBtn.addEventListener('click', () => {
		configContainer.style.display = 'none'
	})

	closeChatContainerBtn.addEventListener('click', () => {
		createChatContainer.style.display = 'none'
	})

	closeGroupContainerBtn.addEventListener('click', () => {
		createGroupContainer.style.display = 'none'
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

	toolkitsSelect.addEventListener('click', () => {
		configContainer.style.display = 'none';
		createChatContainer.style.display = 'none';
		createGroupContainer.style.display = 'none';
	})

	toolkitsSelect.addEventListener('change', event => {
		const tool = event.target.value;
		if (tool === 'create-new-group') {
			createGroupContainer.style.display = "block"
		} else if (tool === 'create-new-chat') {
			createChatContainer.style.display = "block"
		}

	});

	createGroupSubmitBtn.addEventListener("click", () => {
		const groupName = document.getElementById("new-group-name").value;
		if (groupName) {
			fetch('/create_group', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded',
				},
				body: 'group_name=' + encodeURIComponent(groupName) + '&date=' + encodeURIComponent(currentDateTime),
			})
				.then(response => response.text())
				.then(data => {
					// Manejar la respuesta del servidor
					console.log(data);
				})
				.catch(error => {
					console.error('Error:', error);
				});
			createGroupContainer.style.display = "none";
		} else {
			alert("Please enter a group name");
		}
	});
	createChatSubmitBtn.addEventListener('click', function () {
		const chatName = document.getElementById("new-chat-name").value;
		const chatDescription = document.getElementById("new-chat-description").value;

		fetch('/create_chat', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
			},
			body: 'chat_name=' + encodeURIComponent(chatName) + '&chat_description=' + encodeURIComponent(chatDescription) + '&date=' + encodeURIComponent(currentDateTime),
		})
			.then(response => response.text())
			.then(data => {
				// Handle server response
				console.log(data);
			})
			.catch(error => {
				console.error('Error:', error);
			});

		createGroupContainer.style.display = "none";
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

	socket.on('update chat', function (data) {
		processChat(data, 'user-message')
	});

	socket.on("load session", function (data) {
		const groups = data.groups
		const chats = data.chats

	});

	socket.on('notification', function (data) {
		new Notification(data)
	})

	socket.on('response', function (data) {
		if (isLink(data)) {
			// If it's a link, open it in a new tab/window
			window.open(data, '_blank');
		} else {
			processChat(data, 'emma-message');
			if (notificationOption.checked) {
				new Notification(data)
			}

			if (voiceOption.checked) {
				currentUtterance = new SpeechSynthesisUtterance(data);
				window.speechSynthesis.speak(currentUtterance);
			}
		}
	});


	function createCard(type, title, description, imageUrl) {
		// Crear elementos
		var card = document.createElement("div");
		card.className = "row mx-auto my-1 col-10 " + type + "-card";

		var innerRow1 = document.createElement("div");
		innerRow1.className = "row my-2";

		var imageCol = document.createElement("div");
		imageCol.className = "col-1 p-0 my-auto mx-3";

		var image = document.createElement("img");
		image.className = "round_image";
		if (imageUrl === '') {
			image.src = "https://picsum.photos/200/200"
		} else {
			image.src = imageUrl;
		}

		var innerRow2 = document.createElement("div");
		innerRow2.className = "row col-9 p-0 mx-2";

		var cardInfoCol = document.createElement("div");
		cardInfoCol.className = "col-8 card-info m-0 p-0";

		var cardTitle = document.createElement("p");
		cardTitle.className = "card-title my-1";
		cardTitle.textContent = title;

		var cardDescription = document.createElement("p");
		cardDescription.className = "card-description my-0";
		cardDescription.textContent = description;

		var cardControlsCol = document.createElement("div");
		cardControlsCol.className = "col-3 card-controls d-flex p-3 m-0 ml-3 justify-content-center mx-auto";

		var heartButton = document.createElement("button");
		var heartIcon = document.createElement("i");
		heartButton.className = "mx-1"
		heartIcon.className = "ti-heart";
		heartButton.appendChild(heartIcon);

		var moreButton = document.createElement("button");
		var moreIcon = document.createElement("i");
		moreButton.className = "mx-1"
		moreIcon.className = "ti-more";
		moreButton.appendChild(moreIcon);

		if (type === "group") {
			var chatsGroupList = document.createElement("div");
			chatsGroupList.className = "chats-group-list col-11 m-0 p-0";

			var chatsGroupButton = document.createElement("button");
			chatsGroupButton.className = "col-12 px-5";
			var angleDownIcon = document.createElement("i");
			angleDownIcon.className = "ti-angle-down";
			chatsGroupButton.appendChild(angleDownIcon);

			chatsGroupList.appendChild(chatsGroupButton);
			innerRow1.appendChild(chatsGroupList);
		}

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

		return card;
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
		data.forEach(message => {
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
				socket.emit('message', { "message": message, "uid": uid, "device": device_id, "chat_id": chat_id });
				processChat(message, 'user-message');
			}// Assign user message class
		}
	}
	messageInput.addEventListener("keydown", handleKeyDown);


})