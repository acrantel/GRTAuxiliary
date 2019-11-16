// flask url that js should try to send data to (click events)
const postrl = "http://localhost:5000/locationpost";

// flask url that provides all data for drawing
const alldata = "http://localhost:5000/givealldata";

// lidar data is in mm, field dimensions are in inches
const mmToIn = 0.03937008;

// dimension of one lidar point rectangle
const pointWidth = 5;

// any lidar point below this quality will not be used
const qualityThreshold = 30;

// whatever looks good on screen and leaves room for battery levels and time
// if adjusted, change in python file and html canvas dimensions
const scale = 1.7;

var robot = document.getElementById("robot");
var container = document.getElementById("contain");

var canvas = document.getElementById("fieldcanvas");
var ctx = canvas.getContext("2d");

var robotImage = new Image();
robotImage.src = 'static/robot.png';

var fieldImage = new Image();
fieldImage.src = 'static/field.png';

Math.radians = function(degrees) {
    return degrees * Math.PI / 180;
}

//container.addEventListener("click", getClickPosition, false);

// function getClickPosition(e) {
//     $.ajax({
//         type: "POST",
//         url: postrl,
//         contentType: "application/json",
//         data: JSON.stringify({
//             x:e.clientX,
//             y:e.clientY
//         }),
//         dataType: "json",
//         success: function(response) { console.log(response) },
//         error: function(err) { console.log(err) }
//     });
// }

// called every 0.2 seconds by the setInterval, responsible for drawing everything
function drawData(response) {
    // fastest way to clear a canvas
    ctx.clearRect(0,0,canvas.width,canvas.height);

    // draw field to cover entire canvas
    ctx.drawImage(fieldImage, 0, 0, canvas.width, canvas.height);

    // response will in form [pos, lidar]
    let pos = response[0];
    let lidar = response[1];
    
    // draw robot at pos provided, centering it
    ctx.drawImage(robotImage, pos[0]-robotImage.width/2, pos[1]-robotImage.height/2);

    // loop through every lidar point and draw a rectangle for it
    for (var i = 0; i < lidar.length; i++) {
        var point = lidar[i]; // [theta, r , Q]
        // don't use any points that have low quality
        if (point[2] > qualityThreshold) {
            // convert polar to x,y for drawing
            // lidar angles go clockwise so 30 is equal to normally 330
            var x = Math.cos(Math.radians(360 - point[0]))*point[1]*mmToIn*scale;
            var y = (Math.sin(Math.radians(point[0]))*point[1]*mmToIn*scale);

            // center and draw points in green
            ctx.fillStyle = "#00FF00";
            ctx.fillRect(pos[0]+x - pointWidth/2, pos[1]+y - pointWidth/2, pointWidth, pointWidth);
        }
    }
}

// ask for data every 0.2 seconds (refresh rate of lidar)
setInterval(() => {
    $.ajax({
        type: "POST",
        url: alldata,
        contentType: "application/json",
        data: JSON.stringify({}),
        dataType: "json",
        success: function(response) { drawData(response); },
        error: function(err) { console.log(err); }
    });
},75);