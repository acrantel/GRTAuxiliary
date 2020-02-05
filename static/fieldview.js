// flask url that provides all data for drawing
const alldata = "http://"+ip+":5000/giveall/";

// flask url that takes in canvas click data
const clickurl = "http://"+ip+":5000/canvasdata/";

// lidar data is in mm, field dimensions are in inches
const mmToIn = 0.03937008;

// dimension of one lidar point rectangle
const pointWidth = 5;

// any lidar point below this quality will not be used
const qualityThreshold = 30;

// field dimensions in inches
const fieldWidth = 629.25;
const fieldHeight = 323.25;
const widthHeightRatio = fieldWidth / fieldHeight;

let robot = document.getElementById("robot");
let canvasField = document.getElementById("fieldcanvas");
let ctxField = canvasField.getContext("2d");

// 0.7 looks nice, gives space for buttons, and camera aspect ratio looks good
canvasField.height = window.innerHeight * 0.7;
canvasField.width = canvasField.height * widthHeightRatio;
let inchToPx = canvasField.width / fieldWidth

let robotImage = new Image();
robotImage.src = 'static/robot.png';

let fieldImage = new Image();
fieldImage.src = 'static/field.png';

Math.radians = function (degrees) {
    return degrees * Math.PI / 180;
}

canvasField.addEventListener("click", getClickPosition, false);

function getClickPosition(event) {
    const rect = canvasField.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    $.ajax({
        type: "POST",
        url: clickurl,
        contentType: "application/json",
        data: JSON.stringify({x,y}),
        dataType: "json",
        success: function(response) { console.log(response) },
        error: function(err) { console.log(err) }
    });
}


// called very often by the setInterval, responsible for drawing everything on canvas
function drawData(response) {
    // fastest way to clear a canvas
    ctxField.clearRect(0, 0, canvasField.width, canvasField.height);

    // draw field to cover entire canvas
    ctxField.drawImage(fieldImage, 0, 0, canvasField.width, canvasField.height);

    // response will in form [pos, lidar]
    let pos = response[0];
    let lidar = response[1];

    // convert robot pos to pixels and center
    let robotPos = [pos[0] * mmToIn * inchToPx - robotImage.width / 2, pos[1] * mmToIn * inchToPx - robotImage.height / 2]
    ctxField.drawImage(robotImage, robotPos[0], robotPos[1]);
    
    // loop through every lidar point and draw a rectangle for it
    // for (let i = 0; i < lidar.length; i++) {
    //     let point = lidar[i]; // [theta, r , Q]
    //     // don't use any points that have low quality
    //     if (point[2] > qualityThreshold) {

    //         // convert polar to x,y for drawing
    //         // lidar angles go clockwise so 30 is equal to normally 330
    //         // TODO: y might be inverted
    //         let x = Math.cos(Math.radians(-point[0])) * point[1]*mmToIn*inchToPx
    //         let y = Math.sin(Math.radians(-point[0])) * point[1]*mmToIn*inchToPx
    //         let pointPos = [robotPos[0] + x - pointWidth / 2 + robotImage.width / 2, robotPos[1] + y - pointWidth / 2 + robotImage.width / 2]

    //         // center and draw points in green
    //         ctxField.fillStyle = "#00FF00";
    //         ctxField.fillRect(pointPos[0], pointPos[1], pointWidth, pointWidth);
    //     }
    // }
    //console.log(lidar)
    ctxField.beginPath();
    ctxField.lineWidth = 10;
    for (let i = 0; i < lidar.length; i++) {
        let point = lidar[i]
        ctxField.lineTo(inchToPx * point[0], inchToPx * point[1])
    }

    ctxField.stroke()
}

// ask for data every 0.2 seconds (refresh rate of lidar)
setInterval(() => {
    $.ajax({
        type: "GET",
        url: alldata,
        success: function (response) { drawData(response); },
        error: function (err) { console.log(err); }
    });
}, 200);