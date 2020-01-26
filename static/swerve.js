const swervedata = "http://localhost:5000/swervedata/";
const lemondata = "http://localhost:5000/lemondata/";

let canvasSwerve = document.getElementById("swervecanvas");
let ctxSwerve = canvasSwerve.getContext("2d");

canvasSwerve.height = window.innerHeight * 0.5;
canvasSwerve.width = window.innerWidth - (canvasField.height * widthHeightRatio);
lemonCount = 0;

function drawSwerve(response) {
    ctxSwerve.clearRect(0, 0, canvasField.width, canvasField.height);
    ctxSwerve.lineWidth = 10;
    ctxSwerve.beginPath();
    ctxSwerve.rect(canvasSwerve.width * 0.25, canvasSwerve.height * 0.25, canvasSwerve.width * 0.5, canvasSwerve.height * 0.3);
    ctxSwerve.stroke();

    ctxSwerve.textAlign = "center";
    ctxSwerve.fillStyle = "#000000"
    ctxSwerve.font = "40px Comic Sans MS";


    ctxSwerve.fillText("Left", canvasSwerve.width * 0.5, canvasSwerve.height * 0.15);
    ctxSwerve.fillText("Right", canvasSwerve.width * 0.5, canvasSwerve.height * 0.7);

    ctxSwerve.save();
    ctxSwerve.translate(0,0);
    ctxSwerve.rotate(-Math.PI/2);
    ctxSwerve.fillText("Front", -canvasSwerve.height * 0.4, canvasSwerve.width * 0.15);
    ctxSwerve.fillText("Back", -canvasSwerve.height * 0.4, canvasSwerve.width * 0.9);
    ctxSwerve.restore();

    pos = {
        "fl":[canvasSwerve.width * 0.25, canvasSwerve.height * 0.25],
        "fr":[canvasSwerve.width * 0.25, canvasSwerve.height * 0.55],
        "bl":[canvasSwerve.width * 0.75, canvasSwerve.height * 0.25],
        "br":[canvasSwerve.width * 0.75, canvasSwerve.height * 0.55]
    }

    for (let key in response) {
        if (response.hasOwnProperty(key)) {  
            currPos = pos[key]         
            ctxSwerve.beginPath();
            ctxSwerve.arc(currPos[0], currPos[1], 25, 0, 2 * Math.PI)
            if (response[key]) ctxSwerve.fillStyle = "rgba(0, 255, 0, 0.5)"
            else ctxSwerve.fillStyle = "rgba(255, 0, 0, 0.5)"
            ctxSwerve.fill()
        }
    }

    ctxSwerve.fillStyle = "#CECE16"
    for (let i = 0; i < lemonCount; i++) {
        ctxSwerve.beginPath();
        ctxSwerve.arc(canvasSwerve.width*0.1 + i*75, canvasSwerve.height*0.9, 25, 0, 2 * Math.PI)
        ctxSwerve.fill()
    }
}


function setLemon(response) {
    lemonCount = response
}

setInterval(() => {
    $.ajax({
        type: "GET",
        url: swervedata,
        success: function (response) { drawSwerve(response); },
        error: function (err) { console.log(err); }
    });
}, 200);

setInterval(() => {
    $.ajax({
        type: "GET",
        url: lemondata,
        success: function (response) { setLemon(response); },
        error: function (err) { console.log(err); }
    });
}, 200);