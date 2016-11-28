$(document).ready(function() {
    /* set up sortable */
    $(function () {
        $( "ul.sortable" ).sortable();
        $( "ul.sortable" ).disableSelection();
    });

    $( "ul.sortable" ).sortable({
        cancel: "span.not_sortable"
    });

    /* set order for sortable items */
    $("ul#resolution li").each(function () {
        $(this).siblings().eq($(this).attr('sort')).after($(this));
    });
    $("ul#sources li").each(function () {
        $(this).siblings().eq($(this).attr('sort')).after($(this));
    });

    /* set default state for pseudo checkboxes */
    $('i.toggle').each(function(){
       if ( $(this).attr("value") == "true" ){
           $(this).text('check_box');
       }
    });

    /* toggle check box status */
    $('i.toggle').click(function(){
        // turn on
        if( $(this).attr("value") == "false" ){
            $(this).attr("value", "true");
            $(this).text('check_box');
        // turn off
        } else if ( $(this).attr("value") == "true" ){
            $(this).attr("value", "false");
            $(this).text('check_box_outline_blank');
        }
    });


    /* Button actions */
    $('i#close').click(function(e) {
        $('div#overlay').fadeOut();
        $('div#status_pop_up').slideUp();
        $("div#status_pop_up").empty();
        e.preventDefault();
    });

    $('i#remove').click(function(e) {
        var title = $('span#title').text();
        var $this = $(this)

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

    $('i#search_now').click(function(e) {
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

    $('i#change_quality').click(function(){
        $(this).hide();
        $('i#save_quality').show();
        $('ul#result_list').fadeOut();
        $('ul#quality').fadeIn();
    });


    $('i#save_quality').click(function(){
        $this = $(this);

        /* gather information */
        quality_dict = {}
        // QUALITY options. This has a lot of data, so this wil get messy.
        var Quality = {},
            tmp = {};
        var q_list = []
        $("ul#resolution i.toggle").each(function(){
            q_list.push( $(this).attr("id") );
        });

        // enabled resolutions
        $("ul#resolution i.toggle").each(function(){
            tmp[$(this).attr("id")] = $(this).attr("value");
        });
        // order of resolutions
        var arr = $("ul#resolution").sortable("toArray");
        arr.shift();
        $.each(arr, function(i, v){
            tmp[v] = i;
        });
        // min/max sizes
        $("#resolution_size :input").each(function(){
            tmp[$(this).attr("id")] = $(this).val();
        });

        $.each(q_list, function(i, v){
            var enabled = v,
                priority = v + "priority",
                min = v + "min",
                max = v + "max";
            var dt = [tmp[enabled], tmp[priority], tmp[min], tmp[max]]
            Quality[v] = dt.join();
        });

        quality_dict["Quality"] = Quality;

        // FILTERS options.
        var Filters = {};
        $("ul#filters li input").each(function(){
            var val = $(this).val().split(", ").join(",");
            Filters[$(this).attr("id")] = val;
        });
        quality_dict["Filters"] = Filters;

        quality = JSON.stringify(quality_dict);

        var imdbid = $('span#title').attr('imdbid')
        var title = $('i#search_now').attr('title')

        $.post("/update_quality_settings", {"quality": quality, "imdbid": imdbid})
        .done(function(r){
            $this.hide();

            if(r == 'same'){
                console.log(r);
            }
            // if criteria has changed we get passed a time
            else if(r.includes(':')){

                refresh_list('#result_list', imdbid=imdbid);
                refresh_list('#movie_list');

                var search_confirm = confirm("Search criteria has changed and search must run to update search results. The next automatic search is scheduled for "+r+". Would you like to search immediately?")

                if(search_confirm == true){
                    $.post("/search", {"imdbid": imdbid, "title":title})
                }
            }
            // if we get an error message
            else{
                refresh_list('#result_list', imdbid=imdbid);
                refresh_list('#movie_list');

                alert(r);
            }

            $('i#change_quality').show();
            $('ul#result_list').fadeIn();
            $('ul#quality').fadeOut();


        });
    });


/* search result actions */
    $('ul#result_list').on('click', 'i.manual_download', function(e){
        var $this = $(this);
        var download = $this.attr('download');
        var type = $this.attr('type');
        var guid = $this.attr('guid');
        var title = $this.attr('title');
        var imdbid = $('span#title').attr('imdbid')

        $.post("/manual_download", {"guid":guid})
        .done(function(r){
            refresh_list('#movie_list');
            refresh_list('#result_list', imdbid=imdbid)
            alert(r);
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
