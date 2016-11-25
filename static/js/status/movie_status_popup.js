$(document).ready(function() {
    $('button#close').click(function(e) {
        $('div#overlay').fadeOut();
        $('div#status_pop_up').slideUp();
        $("div#status_pop_up").empty();
        e.preventDefault();
    });

    $('button#remove').click(function(e) {
        var title = $('span#title').text();
        var $this = $(this)

        $this.css('background-color', '#212121');
        $this.css('color', 'white');
        $this.width($this.width());
        $this.text('- - -');

        if( confirm('Remove ' + title + '? \nThis will not remove any downloaded movies.')){
            var imdbid = $('span#title').attr('imdbid');
            $.post("/remove_movie", {"imdbid":imdbid})
            .done(function(r){
                if(r == 'error'){
                    alert(title + 'could not be removed. Check logs for more information.')
                }

                refresh_list('#movie_list');
                $('div#status_pop_up').slideUp();
                $('div#overlay').fadeOut();
            });
            e.preventDefault();
        } else {
            return
        }
    });

    $('button#search_now').click(function(e) {
        var imdbid = $(this).attr('imdbid');
        var title = $(this).attr('title');

        $('ul#result_list').hide();
        $('div#results_thinker').show();

        $.post("/search", {"imdbid":imdbid, "title":title})
        .done(function(r){
            refresh_list('#result_list', imdbid=imdbid)
            refresh_list('#movie_list')

            $('div#results_thinker').hide();
        });
        e.preventDefault();
    });

    $('ul#result_list').on('click', 'i.manual_download', function(e){
        var $this = $(this);
        var download = $this.attr('download');
        var type = $this.attr('type');
        var guid = $this.attr('guid');
        var title = $this.attr('title');
        var imdbid = $('span#title').attr('imdbid')

        $.post("/manual_download", {"guid":guid})
        .done(function(response){
            refresh_list('#movie_list');
            refresh_list('#result_list', imdbid=imdbid)
            alert(response);
        });
        e.preventDefault();
    });

    $('ul#result_list').on('click', 'i.mark_bad', function(e) {
        var $this = $(this);

        if( confirm('Mark result as Bad?')){

            var guid = $this.attr('guid');
            var imdbid = $('span#title').attr('imdbid')

            $.post("/mark_bad", {"guid":guid})
            .done(function(r){
                refresh_list('#movie_list');
                refresh_list('#result_list', imdbid=imdbid)
                alert(r);
            });
        };
        e.preventDefault();
    });

    function refresh_list(list, imdbid = ''){
        $.post('/refresh_list', {"list":list, 'imdbid':imdbid})
        .done(function(html){
            $(list).html(html);
            $(list).fadeIn();
        });
    }
});
