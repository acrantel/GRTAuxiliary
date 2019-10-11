const req = new XMLHttpRequest();
const postrl = "http://localhost:5000/locationpost";
const getrl = "http://localhost:5000/locationget";
const obj = { your : "mom" };

var robot = document.getElementById("robot");
var container = document.getElementById("contain");
a = container.addEventListener("click", getClickPosition, false);
console.log(a)
function getClickPosition(e) {
    // console.log(e)
    // var xPosition = e.clientX - (robot.clientWidth / 2);
    // var yPosition = e.clientY - (robot.clientHeight / 2);
     
    // robot.style.left = xPosition + "px";
    // robot.style.top = yPosition + "px";

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

setInterval(() => {
    $.ajax({
        type: "POST",
        url: getrl,
        contentType: "application/json",
        data: JSON.stringify({}),
        dataType: "json",
        success: function(response) { console.log(response) },
        error: function(err) { console.log(err) }
    });
}, 5000);