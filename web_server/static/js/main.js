$(document).ready(function() {
  var form = $('#command-form');
  form.submit(function(event) {
    event.preventDefault(); // prevent form submission
    var textInput = $('#command-input').val(); // get the text input value
    // send the text input value to the server using AJAX
    $.ajax({
      url: '/',
      type: 'POST',
      data: {text_input: textInput},
      dataType: 'json',
      success: function(response) {
        console.log(response);
        // handle the server response here, for example:
        // $('#response-div').html(response.message);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(textStatus, errorThrown);
      }
    });
    // clear the form input
    form[0].reset();
  });
});

var consoleData = [];
var container = $("#console-box");
container.scrollTop(container.prop('scrollHeight'));
setInterval(function() {
$.get("/console", function(data) {
      consoleData.push(data);
  if (Object.keys(data).length === 0) {
        return
      }
  if (consoleData.length > 250) {
        consoleData = consoleData.slice(-250);
        $('#console-content p:first-child').remove();
      }
      var time = getTime();
      var text = "[" + time + "] " + data;
      var consoleText = $('<p>').addClass('console-text').text(text);
      $('#console-content').append(consoleText);
      container.scrollTop(container.prop('scrollHeight'));
    });
  }, 100);


$(document).ready(function() {
    setInterval(function() {
      $.get("/data", function(data) {
        json_data = data
        let server_status = $("#server-status")
        let server_load = $("#server-load")
        let server_threads = $("#server-threads")
        let server_ram = $("#server-ram-usage")
        let server_time = $("#server-time")
        
        server_status.text(json_data.status)
        server_load.text(json_data.cpu_usage)
        server_threads.text(json_data.threads)
        server_ram.text(json_data.memory_usage)
        server_time.text(json_data.time)

      });
    }, 100); 
}); 

function getTime() {
  var now = new Date();
  var hours = now.getHours() % 12 || 12;
  var minutes = now.getMinutes();
  if (minutes < 10) {
    minutes = "0" + minutes;
  }
  var seconds = now.getSeconds();
  if (seconds < 10) {
    seconds = "0" + seconds;
  }
  var meridian = now.getHours() >= 12 ? "PM" : "AM";
  var timeString = hours + ":" + minutes + ":" + seconds + " " + meridian;
  return timeString;
}

function serverTime() {
  var timeString = getTime();
  $('#local-time').html(timeString);
}

setInterval(serverTime, 1000); // Update time every second


