const req = new XMLHttpRequest();
const postrl = "http://localhost:5000/locationpost";
const getrl = "http://localhost:5000/locationget";

var robot = document.getElementById("robot");
var container = document.getElementById("contain");
container.addEventListener("click", getClickPosition, false);

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

function setRobotPosition(response) {
    let xPosition = response.x - (robot.clientWidth / 2);
    let yPosition = response.y - (robot.clientHeight / 2);
    robot.style.left = xPosition + "px";
    robot.style.top = yPosition + "px";
}

// ask for response every 3 seconds
setInterval(() => {
    $.ajax({
        type: "POST",
        url: getrl,
        contentType: "application/json",
        data: JSON.stringify({}),
        dataType: "json",
        success: function(response) { setRobotPosition(response) },
        error: function(err) { console.log(err) }
    });
}, 3000);