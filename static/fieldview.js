var robot = document.getElementById("robot");
var container = document.getElementById("contain");
a = container.addEventListener("click", getClickPosition, false);
console.log(a)
function getClickPosition(e) {
    console.log(e)
    var xPosition = e.clientX - (robot.clientWidth / 2);
    var yPosition = e.clientY - (robot.clientHeight / 2);
     
    robot.style.left = xPosition + "px";
    robot.style.top = yPosition + "px";
}
