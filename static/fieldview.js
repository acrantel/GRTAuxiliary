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

// field is 40 feet long, 20 feet tall -> in inches
const fieldWidth = 40*12
const fieldHeight = 20*12
const widthHeightRatio = fieldWidth / fieldHeight

let robot = document.getElementById("robot");
let container = document.getElementById("contain");

let canvas = document.getElementById("fieldcanvas");
let ctx = canvas.getContext("2d");

// 0.7 looks nice, gives space for buttons, and camera aspect ratio looks good
canvas.height = window.innerHeight * 0.7;
canvas.width = canvas.height * widthHeightRatio;
let inchToPx = canvas.width / fieldWidth

let robotImage = new Image();
robotImage.src = 'static/robot.png';

let fieldImage = new Image();
fieldImage.src = 'static/field.png';

Math.radians = function (degrees) {
    return degrees * Math.PI / 180;
}

// TODO: send click events to java
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

// called every very often by the setInterval, responsible for drawing everything
function drawData(response) {
    // fastest way to clear a canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // draw field to cover entire canvas
    ctx.drawImage(fieldImage, 0, 0, canvas.width, canvas.height);

    // response will in form [pos, lidar]
    let pos = response[0];
    let lidar = response[1];

    // convert robot pos to pixels and center
    let robotPos = [pos[0] * mmToIn * inchToPx - robotImage.width / 2, pos[1] * mmToIn * inchToPx - robotImage.height / 2]
    ctx.drawImage(robotImage, robotPos[0], robotPos[1]);
    
    // loop through every lidar point and draw a rectangle for it
    for (let i = 0; i < lidar.length; i++) {
        let point = lidar[i]; // [theta, r , Q]
        // don't use any points that have low quality
        if (point[2] > qualityThreshold) {

            // convert polar to x,y for drawing
            // lidar angles go clockwise so 30 is equal to normally 330
            // TODO: y might be inverted
            let x = Math.cos(Math.radians(-point[0])) * point[1]*mmToIn*inchToPx
            let y = Math.sin(Math.radians(-point[0])) * point[1]*mmToIn*inchToPx
            let pointPos = [robotPos[0] + x - pointWidth / 2 + robotImage.width / 2, robotPos[1] + y - pointWidth / 2 + robotImage.width / 2]

            // center and draw points in green
            ctx.fillStyle = "#00FF00";
            ctx.fillRect(pointPos[0], pointPos[1], pointWidth, pointWidth);
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
        success: function (response) { drawData(response); },
        error: function (err) { console.log(err); }
    });
}, 200);