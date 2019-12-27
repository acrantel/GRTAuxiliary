// flask url that js should try to send data to (click events)
const postrl = "http://localhost:5000/getbuttondata/"

function buttonClick(id) {
    $.ajax({
        type: "POST",
        url: postrl,
        contentType: "application/json",
        data: JSON.stringify(id),
        dataType: "json",
        success: function(response) { console.log(response) },
        error: function(err) { console.log(err) }
    });
}