$(document).ready(function() {
    var url_base = $("meta[name='url_base']").attr("content");

    // applies add movie overlay
    $("div#content").on("click", "li", function(){
        $("div#overlay").fadeIn();

        imdbid = $(this).attr("imdbid");

        $.post(url_base + "/ajax/movie_status_popup", {"imdbid": imdbid})
            .done(function(html){
                $("div#status_pop_up").html(html);
                $("div#status_pop_up").slideDown();
            });
    });

    $("body").on("click" ,"div#overlay", function(){
        $(this).fadeOut();
        $("div#status_pop_up").slideUp();
        $("div#status_pop_up").empty();
        /* Don"t ask me why slide Up slides it down. I give up. It works. That is all we need to know :) */

    });

});
