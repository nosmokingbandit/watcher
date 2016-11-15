$(document).ready(function () {
    $.post('/server_status', {
        mode: 'restart'
    });

    /*
    This repeats every 3 seconds to check. Times out after 10 attempts and shows error message.
    */
    var try_count = 0
    var check = setInterval(function(){
        if(try_count < 10){
            $.post("/server_status", {
                mode: "online",
            })
            .done(function(r){
                console.log(r);
                if(r == "states.STARTED"){
                    window.location = "/";
                }
            });
        }
        else {
            clearInterval(check);
            $('span.msg').text('');
            $('span.error').show();
            $('#thinker').hide();
        }
    }, 3000);
});

