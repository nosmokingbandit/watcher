$(document).ready(function() {
    var url_base = $("meta[name='url_base']").attr("content");

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

        $.post(url_base + "/ajax/search", {"imdbid":imdbid, "title":title})
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
            confirmButtonColor: "#4CAF50",
            confirmButtonText: "Remove It",
            closeOnConfirm: false
        }, function(){
            var imdbid = $('span#title').attr('imdbid');
            $.post(url_base + "/ajax/remove_movie", {"imdbid":imdbid})
            .done(function(r){
                response = JSON.parse(r)

                if(response["response"] == "false"){
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

        $.post(url_base + "/ajax/update_quality_settings", {"quality": quality_dict, "imdbid": imdbid})
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
                    confirmButtonColor: "#4CAF50",
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
                toastr.error(r);
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
    $('div#status_pop_up').on('click', 'i#manual_download', function(e){
        var $this = $(this);
        var download = $this.attr('download');
        var type = $this.attr('type');
        var guid = $this.attr('guid');
        var title = $this.attr('title');
        var imdbid = $('span#title').attr('imdbid')

        $this.addClass('fa-circle faa-burst animated');

        $.post(url_base + "/ajax/manual_download", {"guid":guid})
        .done(function(r){
            response = JSON.parse(r);
            refresh_list('#movie_list');
            refresh_list('#result_list', imdbid=imdbid)

            if(response['response'] == 'true'){
                toastr.success(response['message']);
            } else {
                toastr.error(response['error']);
            }

            $this.removeClass('fa-circle faa-burst animated');
        });
        e.preventDefault();
    });

    $('div#status_pop_up').on('click', 'i#mark_bad', function(e) {
        var $this = $(this);

        $this.addClass('fa-circle faa-burst animated');
        var guid = $this.attr('guid');
        var imdbid = $('span#title').attr('imdbid')

        $.post(url_base + "/ajax/mark_bad", {
            "guid":guid,
            "imdbid":imdbid
        })
        .done(function(r){
            response = JSON.parse(r);

            refresh_list('#movie_list');
            refresh_list('#result_list', imdbid=imdbid);
            if (response['response'] == 'true'){
                toastr.success(response['message']);
            } else {
                toastr.error(response['error']);
            };
            $this.removeClass('fa-circle faa-burst animated');
        });
    });

    function refresh_list(list, imdbid){
        if(imdbid === undefined) {
            imdbid = '';
        };

        var $list = $(list)
        cls_obj = $list.prop('classList');

        classes = ''

        $.each(cls_obj, function(k,v){
            classes = classes + v + ' '
        })


        $.post(url_base + "/ajax/refresh_list", {"list":list, 'imdbid':imdbid})
        .done(function(html){
            var $parent = $list.parent()
            $list.remove();
            $parent.append(html);
            $(list).addClass(classes);
            if(list == '#movie_list'){
                order = $("select#list_sort").find("option:selected").val();
                $parent = $(list);
                children = 'li';
                sortOrder(order, $parent, children);
            }
        });
    }
});
