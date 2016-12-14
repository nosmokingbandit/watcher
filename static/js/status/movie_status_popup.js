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
    $('i.checkbox').each(function(){
       if ( $(this).attr("value") == "true" ){
           $(this).removeClass('fa-square-o')
           $(this).addClass('fa-check-square-o');
       }
    });

    /* toggle check box status */
    $('i.checkbox').click(function(){
        // turn on
        if( $(this).attr("value") == "false" ){
            $(this).attr("value", "true");
            $(this).removeClass('fa-square-o');
            $(this).addClass('fa-check-square-o');
        // turn off
        } else if ( $(this).attr("value") == "true" ){
            $(this).attr("value", "false");
            $(this).removeClass('fa-check-square-o')
            $(this).addClass('fa-square-o');
        }
    });

    /* Button actions */
    function search_now(imdbid, title){
        $('ul#result_list').hide();
        $('div#results_thinker').show();
        $('i#search_now').addClass('fa-circle faa-burst animated');

        $.post("/search", {"imdbid":imdbid, "title":title})
        .done(function(r){
            refresh_list('#result_list', imdbid=imdbid)
            refresh_list('#movie_list')

            $('div#results_thinker').hide();
            $('i#search_now').removeClass('fa-circle faa-burst animated');

        });
    };

    $('i#close').click(function(e) {
        $('div#overlay').fadeOut();
        $('div#status_pop_up').slideUp();
        $("div#status_pop_up").empty();
        e.preventDefault();
    });

    $('i#remove').click(function(e) {
        var title = $('span#title').text();
        var $this = $(this)

        swal({
            title: "Remove " + title +"?",
            text: "This will not remove any downloaded movies.",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#F44336",
            confirmButtonText: "Remove It",
            closeOnConfirm: false
        }, function(){
            var imdbid = $('span#title').attr('imdbid');
            $.post("/remove_movie", {"imdbid":imdbid})
            .done(function(r){
                if(r == "error"){
                    var message = title + ' could not be removed. Check logs for more information.';
                    swal("Error", message, "error");
                } else {
                    swal.close();
                    refresh_list('#movie_list');
                    $('div#status_pop_up').slideUp();
                    $('div#overlay').fadeOut();
                }
            });
        });
    });

    $('i#search_now').click(function(e) {
        var $this = $(this);
        var imdbid = $this.attr('imdbid');
        var title = $this.attr('title');
        search_now(imdbid, title);
    });

    $('i#change_quality').click(function(){
        $(this).hide();
        $('i#save_quality').show();
        $('i#close').fadeTo(100, 0.5)
        $('i#remove').fadeTo(100, 0.5)
        $('i#search_now').fadeTo(100, 0.5)

        $('ul#result_list').fadeOut();
        $('ul#quality').fadeIn();
    });


    $('i#save_quality').click(function(){
        $this = $(this);
        $this.addClass('fa-circle faa-burst animated');

        /* gather information */
        var quality_dict = {}
        // QUALITY options. This has a lot of data, so this wil get messy.
        var Quality = {},
            tmp = {};
        var q_list = []
        $("ul#resolution i.checkbox").each(function(){
            q_list.push( $(this).attr("id") );
        });

        // enabled resolutions
        $("ul#resolution i.checkbox").each(function(){
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

        $.each(q_list, function(i, res){
            var enabled = res,
                priority = res + "priority",
                min = res + "min",
                max = res + "max";
            var dt = [tmp[enabled], tmp[priority], tmp[min], tmp[max]]
            Quality[res] = [tmp[enabled], tmp[priority], tmp[min], tmp[max]];
        });

        quality_dict["Quality"] = Quality;

        // FILTERS options.
        var Filters = {};
        $("ul#filters li input").each(function(){
            var val = $(this).val().split(", ").join(",");
            Filters[$(this).attr("id")] = val;
        });
        quality_dict["Filters"] = Filters;

        var quality_dict = JSON.stringify(quality_dict);

        var imdbid = $('span#title').attr('imdbid');
        var title = $('i#search_now').attr('title');

        $.post("/update_quality_settings", {"quality": quality_dict, "imdbid": imdbid})
        .done(function(r){
            refresh_list('#result_list', imdbid=imdbid);
            refresh_list('#movie_list');

            if(r == 'same'){ /* do nothing */ }
            // if criteria has changed we get passed a time
            else if(r.includes(':')){

                refresh_list('#result_list', imdbid=imdbid);
                refresh_list('#movie_list');

                swal({
                    title: "Search Now?",
                    text: "Search criteria has changed and search must run to update results. <br/> The next automatic search is scheduled for "+r+". Would you like to search immediately?",
                    html: true,
                    type: "warning",
                    showCancelButton: true,
                    cancelButtonText: "Wait",
                    confirmButtonColor: "#F44336",
                    confirmButtonText: "Search Now",
                    closeOnConfirm: true
                }, function(){
                    search_now(imdbid, title);
                })
            }
            // if we get an error message
            else{
                refresh_list('#result_list', imdbid=imdbid);
                refresh_list('#movie_list');
                swal("Error", r, "error");
            };

            $this.removeClass('fa-circle faa-burst animated');
            $this.hide();

            $('i#close').fadeTo(100, 1)
            $('i#remove').fadeTo(100, 1)
            $('i#search_now').fadeTo(100, 1)

            $('i#change_quality').show();
            $('ul#result_list').fadeIn();
            $('ul#quality').fadeOut();


        });
    });


/* search result actions */
    $('ul#result_list').on('click', 'i#manual_download', function(e){
        var $this = $(this);
        var download = $this.attr('download');
        var type = $this.attr('type');
        var guid = $this.attr('guid');
        var title = $this.attr('title');
        var imdbid = $('span#title').attr('imdbid')

        $this.addClass('fa-circle faa-burst animated');

        $.post("/manual_download", {"guid":guid})
        .done(function(r){
            refresh_list('#movie_list');
            refresh_list('#result_list', imdbid=imdbid)
            swal("", r, "success");
            $this.removeClass('fa-circle faa-burst animated');
        });
        e.preventDefault();
    });

    $('ul#result_list').on('click', 'i#mark_bad', function(e) {
        var $this = $(this);

        swal({
            title: "Mark result as Bad?",
            text: "",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#F44336",
            confirmButtonText: "Mark Bad",
            closeOnConfirm: false
            }, function(){
                $this.addClass('fa-circle faa-burst animated');
                var guid = $this.attr('guid');
                var imdbid = $('span#title').attr('imdbid')

                $.post("/mark_bad", {
                    "guid":guid,
                    "imdbid":imdbid
                })
                .done(function(r){
                    refresh_list('#movie_list');
                    refresh_list('#result_list', imdbid=imdbid);
                    if (r.includes("Success")){
                        swal("", r, "success");
                    } else {
                        swal("", r, "error");
                    };
                    $this.removeClass('fa-circle faa-burst animated');
                });
            }
        );
    });

    function refresh_list(list, imdbid = ''){
        $.post('/refresh_list', {"list":list, 'imdbid':imdbid})
        .done(function(html){
            $(list).html(html);
            $(list).fadeIn();
        });
    }
});
