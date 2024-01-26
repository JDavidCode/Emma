document.addEventListener('DOMContentLoaded', function () {
	var cardWrapper = document.querySelector('.card-3d-wrapper');
	var loginForm = cardWrapper.querySelector('.card-front');
	var signupForm = cardWrapper.querySelector('.card-back');
	const loginBtn = document.getElementById('login-btn')
	const signUpBtn = document.getElementById('signup-btn')


	// Event listener for the login button
	loginBtn.addEventListener('click', function (e) {
		e.preventDefault();

		// Get login form values
		var email = loginForm.querySelector('#logemail').value;
		var password = loginForm.querySelector('#logpass').value;

		// Perform login logic
		console.log('Performing login...');

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
				// Handle the server response
				console.log('Server response:', data);
				loginForm.querySelector('#logemail').value = '';
				loginForm.querySelector('#logpass').value = '';
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

		// Perform signup logic
		console.log('Performing signup...');

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
				}
				signupForm.querySelector('#logname').value = '';
				signupForm.querySelector('#logemail').value = '';
				signupForm.querySelector('#logdate').value = '';
				signupForm.querySelector('#logpass').value = '';

			})
			.catch(error => {
				console.error('Error:', error);
			});

	});
});
