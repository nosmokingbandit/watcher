$(document).ready(function() {
    var movie_results_dict = {};
// sends post to SearchDatabase.post() in main.py and displays results

    $("#search_input").keyup(function(event){
        if(event.keyCode == 13){
            $("#search_button").click();
        }
    });

    $("#search_button").click(function(e) {
        if ( $("input[name='search_term']").val() == "" ){
            return false;
        }

        // if it is open, hide it first. makes it pretty
        if ( $("#database_results").css("display") == "block" ){
            $("#database_results").hide();
            $("#movie_list").empty();
        }

        $('#thinker').fadeIn();

        $.post("/search_omdb", {
            "search_term":              $("input[name='search_term']").val()
        })

        .done(function(l) {
            if (l != ''){
                movie_results_dict = JSON.parse(l);
                l = JSON.parse(l);
                var results_html;
                var movie_list = $("#movie_list")
                // move this to a py template or just have the post function return the html ?
                $.each(l, function(ind, dict){
                    $('<li>', {class: 'movie',imdbid: dict['imdbID']}).append(
                        $('<span>').append(
                            $('<img>', {src:dict['Poster']}),
                            dict['Title'],' ',dict['Year'].slice(0,4)
                        )
                    ).appendTo(movie_list)
                });
            }

            $("#database_results").fadeIn();
            $('#thinker').fadeOut();
        });

        e.preventDefault();
    });

// applies add movie overlay

    $('div#database_results').on('click', 'li', function(){
        $('div#overlay').fadeIn();

        imdbid = $(this).attr('imdbid')

        $.post('/movie_info_popup', {'imdbid': imdbid})
            .done(function(html){
                $('div#info_pop_up').html(html);
                $('div#info_pop_up').slideDown();
            });
    });

    $('body').on('click' ,'div#overlay', function(){
        $(this).fadeOut();
        $('div#info_pop_up').slideUp();
        $("div#info_pop_up").empty();
        /* Don't ask me why slide Up slides it down. I give up. It works. That is all we need to know */

    });
});
