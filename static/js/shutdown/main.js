$(document).ready(function () {
    $.post("/server_status", {
        "mode": "shutdown"
    });

    /*
    This repeats every 3 seconds to check. Eventually I"ll put a counter in that shows an error message if it takes too long to restart.
    */
    var check = setInterval(function(){
        $.post("/server_status", {
            "mode": "online",
        })
        .done(function(r){
            //do nothing
        })
        .fail(function(r){
            $("span.msg").fadeOut();
            $("#thinker").fadeOut();
            clearInterval(check);
        })
    }, 3000);
});

