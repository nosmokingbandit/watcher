$(document).ready(function() {
    var url_base = $("meta[name='url_base']").attr("content");

// sends post to SearchDatabase.post() in main.py and displays results

    $("#search_input").keyup(function(event){
        if(event.keyCode == 13){
            $("#search_button").click();
        }
    });

    $("#search_button").click(function(e) {
        var movie_results_dict = {};
        if ( $("input[name='search_term']").val() == "" ){
            return false;
        }

        // if it is open, hide it first. makes it pretty
        if ( $("#database_results").css("display") == "block" ){
            $("#database_results").hide();
            $("#movie_list").empty();
        }

        $('#thinker').fadeIn();

        $.post(url_base + "/ajax/search_omdb", {
            "search_term": $("input[name='search_term']").val()
        })

        .done(function(l) {
            if (l != ''){
                movie_results_dict = JSON.parse(l);
                l = JSON.parse(l);
                var results_html;
                var movie_list = $("#movie_list")
                // move this to a py template or just have the post function return the html ?
                $.each(l, function(ind, dict){
                    $('<li>', {class: 'movie'}).append(
                        $('<span>').append(
                            $("<span>", {class:'quickadd',imdbid: dict['imdbID']})
                                .append(
                                $("<span>", {class: 'quickadd_text'}).text('Quick-Add'),
                                $("<i>", {class: 'fa fa-plus button_add'})
                                ),
                            $('<img>', {src:dict['Poster'],imdbid: dict['imdbID']}),
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

// quickadd buttons
    $("ul#movie_list").on("mouseenter", "span.quickadd", function(){
        $(this).children("span.quickadd_text").stop(true, true).animate(
            {width: 'toggle'}
        )
    });

    $("ul#movie_list").on("mouseleave", "span.quickadd", function(){
        $(this).children("span.quickadd_text").stop(true, true).animate(
            {width: 'toggle'}
        )
    });

    $("ul#movie_list").on("click", "span.quickadd", function(){
        imdbid = $(this).attr('imdbid');

        $icon = $(this).children("i");
        $icon.removeClass('fa-plus');
        $icon.addClass('fa-circle faa-burst animated');

        $.post(url_base + "/ajax/quick_add", {"imdbid":imdbid})
        .done(function(r){
            response = JSON.parse(r)

            $icon.removeClass('fa-circle faa-burst animated');
            $icon.addClass('fa-plus');

            if(response['response'] == 'true'){
                swal("", response['message'], 'success');
            } else {
                swal("", response['message'], 'error');
            };
        })
    });

// applies add movie overlay

    $('div#database_results').on('click', 'img', function(){
        $('div#overlay').fadeIn();

        imdbid = $(this).attr('imdbid')

        $.post(url_base + "/ajax/movie_info_popup", {'imdbid': imdbid})
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
