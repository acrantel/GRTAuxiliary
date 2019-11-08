const postrl = "http://localhost:5000/locationpost";
const alldata = "http://localhost:5000/givedata";
const mmToIn = 0.03937008;
const scale = 1.7;

var robot = document.getElementById("robot");
var container = document.getElementById("contain");

var canvas = document.getElementById("fieldcanvas");
var ctx = canvas.getContext("2d");

var robotWidth = 40;

var robot_image = new Image();
robot_image.src = 'static/robot.png';

container.addEventListener("click", getClickPosition, false);

Math.radians = function(degrees) {
    return degrees * Math.PI / 180;
}

function getClickPosition(e) {
    $.ajax({
        type: "POST",
        url: postrl,
        contentType: "application/json",
        data: JSON.stringify({
            x:e.clientX,
            y:e.clientY
        }),
        dataType: "json",
        success: function(response) { console.log(response) },
        error: function(err) { console.log(err) }
    });
}

function drawData(response) {
    lidar = response[0];
    pos = response[1];
    ctx.drawImage(robot_image, pos[0] - robot_image.naturalWidth/2, pos[1] - robot_image.naturalHeight/2)

    const pointWidth = 5;
    const qualityThreshold = 30;
    for (var i = 0; i < lidar.length; i++) {
        var point = lidar[i]; // [theta, r , Q]
        if (point[2] > qualityThreshold) {
            var x = Math.cos(Math.radians(point[0]))*point[1]*mmToIn*scale;
            var y = Math.sin(Math.radians(point[0]))*point[1]*mmToIn*scale;
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
        success: function(response) { drawData(response) },
        error: function(err) { console.log(err) }
    });
}, 200);