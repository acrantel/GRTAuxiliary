const swervedata = "http://"+ip+":5000/swervedata/"
const lemondata = "http://"+ip+":5000/lemondata/"
const angledata = "http://"+ip+":5000/angledata/"

let canvasSwerve = document.getElementById("swervecanvas");
let ctxSwerve = canvasSwerve.getContext("2d");

canvasSwerve.height = window.innerHeight * 0.5;
canvasSwerve.width = window.innerWidth - (canvasField.height * widthHeightRatio);
lemonCount = 0;
robotAngle = 0;

function drawSwerve(response) {
    ctxSwerve.clearRect(0, 0, canvasField.width, canvasField.height);
    ctxSwerve.lineWidth = 10;
    let widthBox = canvasSwerve.width * 0.4
    let heightBox = canvasSwerve.width * 0.3
    let xStartBox = canvasSwerve.width * 0.3
    let yStartBox = canvasSwerve.width * 0.2

    ctxSwerve.save();
    ctxSwerve.translate(xStartBox+widthBox/2, yStartBox+heightBox/2);
    let radians = ((robotAngle + 90) % 360) * Math.PI / 180;
    ctxSwerve.rotate(radians);
    ctxSwerve.beginPath();
    ctxSwerve.rect(-widthBox / 2, -heightBox / 2, widthBox, heightBox);
    ctxSwerve.stroke();

    pos = {
        "fr":[-widthBox / 2, -heightBox / 2],
        "br":[widthBox / 2, -heightBox / 2],
        "fl":[-widthBox / 2, heightBox / 2],
        "bl":[widthBox / 2, heightBox / 2]
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

    ctxSwerve.textAlign = "center";
    ctxSwerve.fillStyle = "#000000"
    ctxSwerve.font = "30px Comic Sans MS";

    ctxSwerve.rotate(-Math.PI / 2);
    ctxSwerve.fillText("Front", 0,-widthBox / 2 - 20);
    ctxSwerve.rotate(Math.PI);
    ctxSwerve.fillText("Back", 0,-widthBox / 2 - 20);

    ctxSwerve.rotate(-Math.PI / 2);
    ctxSwerve.fillText("Right", 0,-widthBox / 2);
    ctxSwerve.rotate(Math.PI);
    ctxSwerve.fillText("Left", 0,-widthBox / 2);

    ctxSwerve.restore();

    ctxSwerve.textAlign = "center";
    ctxSwerve.fillStyle = "#000000"
    ctxSwerve.font = "30px Comic Sans MS";


    //ctxSwerve.fillText("Left", canvasSwerve.width * 0.5, canvasSwerve.height * 0.15);
    // ctxSwerve.fillText("Right", canvasSwerve.width * 0.5, canvasSwerve.height * 0.7);

    // ctxSwerve.save();
    // ctxSwerve.translate(0,0);
    // ctxSwerve.rotate(-Math.PI/2);
    // ctxSwerve.fillText("Front", -canvasSwerve.height * 0.4, canvasSwerve.width * 0.15);
    // ctxSwerve.fillText("Back", -canvasSwerve.height * 0.4, canvasSwerve.width * 0.9);
    // ctxSwerve.restore();

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

function setAngle(response) {
    robotAngle = response
}

setInterval(() => {
    $.ajax({
        type: "GET",
        url: swervedata,
        success: function (response) { drawSwerve(response); },
        error: function (err) { console.log(err); }
    });
}, 25);

setInterval(() => {
    $.ajax({
        type: "GET",
        url: lemondata,
        success: function (response) { setLemon(response); },
        error: function (err) { console.log(err); }
    });
}, 25);

setInterval(() => {
    $.ajax({
        type: "GET",
        url: angledata,
        success: function (response) { setAngle(response); },
        error: function (err) { console.log(err); }
    });
}, 25);