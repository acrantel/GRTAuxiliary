// flask url that js should try to send data to (click events)
const buttonurl = "http://localhost:5000/getbutton/"

function buttonClick(id) {
    $.ajax({
        type: "POST",
        url: buttonurl,
        contentType: "application/json",
        data: JSON.stringify(id),
        dataType: "json",
        success: function(response) { console.log(response) },
        error: function(err) { console.log(err) }
    });
}