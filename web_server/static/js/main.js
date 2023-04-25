document.addEventListener('DOMContentLoaded', function() {
  var form = document.getElementById('command-form');
  form.addEventListener('submit', function(event) {
    event.preventDefault(); // prevent form submission
    var formData = new FormData(form);
    var textInput = formData.get('text_input'); // get the text input value
    // send the text input value to the server using AJAX
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.send('text_input=' + encodeURIComponent(textInput));
    // clear the form input
    form.reset();
  });
});

var json_data 

$(document).ready(function() {
    setInterval(function() {
      $.get("/data", function(data) {
        json_data =data
      });
    }, 5000); // fetch data every 5 seconds
});

function serverTime() {
    let now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    let seconds = now.getSeconds();
    let meridian = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    seconds = seconds < 10 ? '0' + seconds : seconds;
    let timeString = hours + ':' + minutes + ':' + seconds + ' ' + meridian;
    document.getElementById('local-time').innerHTML = timeString;
  }

  setInterval(serverTime, 1000); // Update time every second
