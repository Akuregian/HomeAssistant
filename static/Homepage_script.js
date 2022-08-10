// Grabs the JSON data from the web-page
$(document).ready(function () {
    console.log("Hello, welcome");
    $.getJSON('http://localhost:5001/devices', function (data) {
        $.each(data.data, function (index, obj) {
            console.log(obj)
            $(".display_dock").append("<div class=display>" + obj.identifier + "</div>");
        })
    });
});