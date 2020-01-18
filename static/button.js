// flask url that js should try to send data to (click events)
const buttonurl = "http://localhost:5000/buttondata/"
const timerurl = "http://localhost:5000/starttimer/"

function buttonClick(id) {
  $.ajax({
    type: "POST",
    url: buttonurl,
    contentType: "application/json",
    data: JSON.stringify(id),
    dataType: "json",
    success: function (response) { console.log(response) },
    error: function (err) { console.log(err) }
  });
}

// Matches are 2:30 or 150 seconds
const timerLength = 150;

function startTimer() {
  end = Math.floor(new Date().getTime() / 1000) + timerLength
  var x = setInterval(function () {
    // Get today's time (in ms so divide by 1000 to get seconds)
    var now = Math.floor(new Date().getTime() / 1000)

    // Find the distance between now and end of game
    var distance = end - now
    console.log(distance)

    // Time calculations for minutes and seconds
    var minutes = Math.floor((distance % (60 * 60)) / 60)
    var seconds = Math.floor(distance % 60)

    // Display the result
    document.getElementById("timer").innerHTML = minutes + "m " + seconds + "s "

    // Depending on time left in game, display correct phase
    // Auton - beginning 15 seconds, Endgame - last 30 seconds
    let currPhase = "Autonomous"
    if (distance <= timerLength - 120) {
      currPhase = "Endgame"
    } else if (distance <= timerLength - 15) {
      currPhase = "Teleop"
    }

    document.getElementById("phase").innerHTML = currPhase

    // If the timer is finished, write some text and stop timer
    if (distance < 0) {
      clearInterval(x)
      document.getElementById("timer").innerHTML = "FINISH"
      document.getElementById("phase").innerHTML = "FINISH"
    }
  }, 1000);
}


// ask for timer start every 1 seconds (arbritrary, can be faster)

let i = setInterval(() => {
  $.ajax({
    type: "GET",
    url: timerurl,
    success: function (response) {
      if (response != 'false') {
        clearInterval(i)
        startTimer()
      }
    },
    error: function (err) { console.log(err); }
  });
}, 1000); 