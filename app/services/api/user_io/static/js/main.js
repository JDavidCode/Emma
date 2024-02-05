document.addEventListener('DOMContentLoaded', function () {
	let uid;
	let socket;
	const currentDateTime = new Date();
	let channelsDict = {};
	let groupsDict = {};
	let chatsDict = {};
	let userInfo;
	let socket_id;
	let currentUtterance;


	const focusLayer = document.getElementById('focus-layer');

	///CONFIG
	const configBtn = document.getElementById('config-btn');
	const configContainer = document.getElementById('config-container');
	const closeConfigBtn = document.getElementById('close-config-btn')
	const themeSelect = document.getElementById("theme-select");
	const voiceOption = document.getElementById("voice-toggle");
	const notificationOption = document.getElementById("notification-toggle");

	//LOGIN PAGE
	var cardWrapper = document.querySelector('.card-3d-wrapper');
	var loginForm = cardWrapper.querySelector('.login-card-front');
	var signupForm = cardWrapper.querySelector('.signup-card-back');
	const loginBtn = document.getElementById('login-btn');
	const signUpBtn = document.getElementById('signup-btn');

	//MAIN HEADER
	const loginArticle = document.getElementById('login');
	const homeArticle = document.getElementById('home');

	const chatsSelectorBtn = document.getElementById("chats-selector-btn");
	const channelsSelectorBtn = document.getElementById("channels-selector-btn");

	const checkSelector = document.getElementById("chats-channels")
	const chatsGroupsContainer = document.getElementById("chats-groups-card-front")
	const chatElements = document.querySelectorAll('.chat-card, .group-card');
	const channelsContainer = document.getElementById("channels-card-back")
	const loader = document.getElementById("loader")

	///TOOLKITS
	const createChatBtn = document.getElementById("create-chat-btn");
	const createGroupBtn = document.getElementById("create-group-btn");
	const createChannelBtn = document.getElementById("create-channel-btn");

	const createChatContainer = document.getElementById('new-chat-container');
	const createGroupContainerBtn = document.getElementById("new-group-container");
	const createChannelContainerBtn = document.getElementById("new-channel-container");

	const createChatSubmitBtn = document.getElementById('create-chat-submit-btn');
	const createGroupSubmitBtn = document.getElementById('create-group-submit-btn');
	const createChannelsubmitBtn = document.getElementById("create-channel-submit-btn");

	const closeChatContainerBtn = document.getElementById('close-new-chat-container-btn');
	const closeGroupContainerBtn = document.getElementById('close-new-group-container-btn')
	const closeChannelContainerBtn = document.getElementById('close-new-channel-container-btn');

	///CHAT
	const chatBox = document.getElementById("chat-content-box")

	///CHAT INPUTS
	const attachDocs = document.getElementById("attach-docs");
	const messageInput = document.getElementById("message-input");
	const messageSend = document.getElementById("message-send");
	const speakBtn = document.getElementById('message-speak');


	function animateLoad() {
		loginArticle.classList.add('fade-out');
		loginArticle.addEventListener('transitionend', function () {
			loginArticle.classList.add('hidden');
		});
		loader.style.display = "flex";

	}

	chatElements.forEach(chatElement => {
		// Find the select element within each chat element
		const selectElement = chatElement.querySelector('.more-btn');

		// Find the card title element within each chat element
		const cardTitleElement = chatElement.querySelector('.card-title');
		const isChatCard = chatElement.classList.contains('chat-card');
		const isGroupCard = chatElement.classList.contains('group-card');
		// Add an event listener to the select element
		selectElement.addEventListener('change', function () {
			// Get the selected value
			const selectedValue = this.value;

			// Get the name of the card associated with the chat
			const cardName = cardTitleElement.innerText;
			console.log(cardName)

			// Perform actions based on the selected value and card name
			if (selectedValue === 'Remove') {
				if (isChatCard) {
					deleteChat(cardName)
				} else if (isGroupCard) {
					deleteGroup(cardName)
				}
			} else if (selectedValue === 'Edit') {
				if (isChatCard) {
					editChat(cardName)
				} else if (isGroupCard) {
					editGroup(cardName)
				}
			}
		});
	});


	function animateTransition() {
		loginArticle.classList.remove('fade-out');
		loader.classList.add('hidden');

		// Después de que se oculta, mostrar el artículo de inicio
		homeArticle.classList.remove('hidden');
		homeArticle.classList.add('fade-in');
	}

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
	createChatBtn.addEventListener('click', () => {
		createChatContainer.style.display = 'block';

	});
	createGroupBtn.addEventListener('click', () => {
		createGroupContainerBtn.style.display = 'block';

	});

	chatsSelectorBtn.addEventListener('click', () => {
		if (checkSelector.checked) {
			checkSelector.checked = !checkSelector.checked;
		}
	});
	channelsSelectorBtn.addEventListener('click', () => {
		if (!checkSelector.checked) {
			checkSelector.checked = !checkSelector.checked;
		}
	});

	configBtn.addEventListener('click', () => {
		configContainer.style.display = configContainer.style.display === "block" ? "none" : "block";
	})

	closeConfigBtn.addEventListener('click', () => {
		configContainer.style.display = 'none';
	})

	closeChatContainerBtn.addEventListener('click', () => {
		createChatContainer.style.display = 'none';
	})

	closeGroupContainerBtn.addEventListener('click', () => {
		createGroupContainerBtn.style.display = 'none';
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


	createChatSubmitBtn.addEventListener('click', function () {
		const chatName = document.getElementById("new-chat-name").value;
		const chatDescription = document.getElementById("new-chat-description").value;

		fetch('/create_chat', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
			},
			body: 'chat_name=' + encodeURIComponent(chatName) + '&chat_description=' + encodeURIComponent(chatDescription) + '&date=' + encodeURIComponent(currentDateTime) + "&uid=" + encodeURIComponent(uid) + "&gid=" + encodeURIComponent,
		})
			.then(response => response.text())
			.then(data => {
				// Handle server response
				console.log(data);
			})
			.catch(error => {
				console.error('Error:', error);
			});

		createChatContainer.style.display = 'none';
	});

	function deleteChat(chat_name) {
		let cid;
		let gid;
		fetch('/delete_chat', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
			},
			body: 'cid=' + encodeURIComponent(cid) + '&gid=' + encodeURIComponent(gid) + '&uid=' + encodeURIComponent(uid),
		})
			.then(response => response.text())
			.then(data => {
				// Handle server response
				console.log(data);
			})
			.catch(error => {
				console.error('Error:', error);
			});

	};

	function editChat(chat_name) {
		let cid;
		let gid;
		fetch('/edit_chat', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
			},
			body: 'cid=' + encodeURIComponent(cid) + '&gid=' + encodeURIComponent(gid) + '&uid=' + encodeURIComponent(uid),
		})
			.then(response => response.text())
			.then(data => {
				// Handle server response
				console.log(data);
			})
			.catch(error => {
				console.error('Error:', error);
			});

	};

	createGroupSubmitBtn.addEventListener("click", () => {
		const groupName = document.getElementById("new-group-name").value;
		const groupDescription = document.getElementById("new-group-description").value;

		if (groupName) {
			fetch('/create_group', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded',
				},
				body: 'group_name=' + encodeURIComponent(groupName) + '&group_description=' + encodeURIComponent(groupDescription) + "&uid=" + encodeURIComponent(uid) + '&date=' + encodeURIComponent(currentDateTime),
			})
				.then(response => response.text())
				.then(data => {
					// Manejar la respuesta del servidor
					console.log(data);
				})
				.catch(error => {
					console.error('Error:', error);
				});
			createGroupContainerBtn.style.display = "none";
		} else {
			alert("Please enter a Group name");
		}
	});


	function deleteGroup(group_name) {
		let gid;
		fetch('/delete_group', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
			},
			body: 'gid=' + encodeURIComponent(gid) + '&uid=' + encodeURIComponent(uid),
		})
			.then(response => response.text())
			.then(data => {
				// Handle server response
				console.log(data);
			})
			.catch(error => {
				console.error('Error:', error);
			});

	};

	function editGroup(chat_name) {
		let cid;
		let gid;
		fetch('/edit_group', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded',
			},
			body: 'gid=' + encodeURIComponent(gid) + '&uid=' + encodeURIComponent(uid),
		})
			.then(response => response.text())
			.then(data => {
				// Handle server response
				console.log(data);
			})
			.catch(error => {
				console.error('Error:', error);
			});

	};

	// Event listener for the login button
	loginBtn.addEventListener('click', function (e) {
		e.preventDefault();

		// Get login form values
		var email = loginForm.querySelector('#logemail').value;
		var password = loginForm.querySelector('#logpass').value;


		fetch('/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				email: email,
				password: password,
			}),
		})
			.then(response => response.json())
			.then(data => {
				if (data.uid) {
					uid = data.uid
					loginForm.querySelector('#logemail').value = '';
					loginForm.querySelector('#logpass').value = '';
					animateLoad();
					socket = io.connect('');
					startSocket();
				} else {
					console.log(data)
				}


			})
			.catch(error => {
				console.error('Error:', error);
			});


	});

	// Event listener for the signup button
	signUpBtn.addEventListener('click', function (e) {
		e.preventDefault();

		// Get signup form values
		var name = signupForm.querySelector('#logname').value;
		var email = signupForm.querySelector('#logemail').value;
		var date = signupForm.querySelector('#logdate').value;
		var password = signupForm.querySelector('#logpass').value;

		fetch('/signup', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				name: name,
				email: email,
				date: date,
				password: password,
			}),
		})
			.then(response => response.json())
			.then(data => {
				if (data) {
					cardWrapper.classList.add('flipped');
					signupForm.querySelector('#logname').value = '';
					signupForm.querySelector('#logemail').value = '';
					signupForm.querySelector('#logdate').value = '';
					signupForm.querySelector('#logpass').value = '';
				}

			})
			.catch(error => {
				console.error('Error:', error);
			});

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

	function startSocket() {
		socket.on('update chat', function (data) {
			processChat(data, 'user-message')
		});

		socket.on("get_user", function (data) {
			if (!userInfo) {
				userInfo = JSON.stringify(data.info, null, 2);
				console.log("this is user info: " + userInfo);
			}

			// Use Sets to store unique group and chat IDs
			const uniqueGroupIds = new Set(Object.keys(groupsDict));
			const uniqueChatIds = new Set(Object.keys(chatsDict));

			// Process and create cards for groups
			for (const group of data.groups) {
				const groupId = group.id;

				if (!uniqueGroupIds.has(groupId)) {
					// Code inside the if block
					uniqueGroupIds.add(groupId);
					groupsDict[groupId] = group.content;
					createCard("", group.group_name, 'group');
				}
			}

			// Process and create cards for chats
			for (const chat of data.chats) {
				const chatId = chat.id;
				if (!uniqueChatIds.has(chatId)) {
					// Code inside the if block
					uniqueChatIds.add(chatId);
					chatsDict[chatId] = chat;
					createCard("", chat.name, 'chat');
				}
			}

			animateTransition();
		});


		socket.on('notification', function (data) {
			new Notification(data)
		});

		socket.on('start_connection', function (data) {
			socket_id = data.client_id // show it bottom with the user id
			console.log("This is socket id" + socket_id)
			socket.emit('get_user', { uid: uid })
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

	}

	function createCard(imageUrl, title, type) {
		// Create main card div
		var cardDiv = document.createElement("div");
		cardDiv.className = "row mx-auto my-3 col-11 " + type + "-card";

		// Create image div
		var imageDiv = document.createElement("div");
		imageDiv.className = "col-1 p-0 my-auto ml-1 mr-2 py-1";
		var image = document.createElement("img");
		image.className = "round_image";
		image.src = imageUrl || "https://picsum.photos/200/200";
		imageDiv.appendChild(image);
		cardDiv.appendChild(imageDiv);

		// Create card info div
		var infoDiv = document.createElement("div");
		infoDiv.className = "col-7 card-info my-auto p-0 ml-3";
		var titlePara = document.createElement("p");
		titlePara.className = "card-title my-auto";
		titlePara.textContent = title;
		infoDiv.appendChild(titlePara);
		cardDiv.appendChild(infoDiv);

		// Create card controls div
		var controlsDiv = document.createElement("div");
		controlsDiv.className = "col-2 card-controls d-flex p-0 m-0 ml-3 align-items-center";
		var select = document.createElement("select");
		select.className = "mx-1 more-btn btn col-12 p-0 m-0 btn px-2 down-btn";

		var defaultOption = document.createElement("option");
		defaultOption.value = "";
		defaultOption.textContent = "";
		defaultOption.disabled = true;
		defaultOption.selected = true;
		defaultOption.style.display = "none";
		select.appendChild(defaultOption);
		// Create options for the select element
		var removeOption = document.createElement("option");
		removeOption.value = "Remove";
		removeOption.textContent = "Remove";
		select.appendChild(removeOption);

		var editOption = document.createElement("option");
		editOption.value = "Edit";
		editOption.textContent = "Edit";
		select.appendChild(editOption);

		controlsDiv.appendChild(select);
		cardDiv.appendChild(controlsDiv);

		if (type === 'group') {
			// Create chats group list button
			var chatsBtn = document.createElement("button");
			chatsBtn.className = "chats-group-list col-12 p-0 m-0 btn px-2 down-btn";
			cardDiv.appendChild(chatsBtn);
			// Assuming there's a container for chatsGroups
			chatsGroupsContainer.appendChild(cardDiv);
		} else if (type === 'chat' || type === 'channels') {
			// Assuming there's a container for chatsGroups
			chatsGroupsContainer.appendChild(cardDiv);
		}
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
			speakBtn.style.display = 'block';
			messageSend.style.display = 'none';

		} else {
			speakBtn.style.display = 'none';
			messageSend.style.display = 'block';
		}
	}
	verifyInputState();
	setInterval(verifyInputState, 500);

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