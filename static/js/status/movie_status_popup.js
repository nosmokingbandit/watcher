$(document).ready(function() {
    var url_base = $("meta[name='url_base']").attr("content");
    $('div#status_pop_up').off();

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
       if ( $(this).attr("value") == "True" ){
           $(this).removeClass('fa-square-o')
           $(this).addClass('fa-check-square');
       }
    });

    /* toggle check box status */
    $('i.checkbox').click(function(){
        // turn on
        if( $(this).attr("value") == "False" ){
            $(this).attr("value", "True");
            $(this).removeClass('fa-square-o');
            $(this).addClass('fa-check-square');
        // turn off
        } else if ( $(this).attr("value") == "True" ){
            $(this).attr("value", "False");
            $(this).removeClass('fa-check-square')
            $(this).addClass('fa-square-o');
        }
    });

    /* Button actions */
    function search_now(imdbid, title, quality){
        $('ul#result_list').hide();
        $('div#results_thinker').show();
        $('i#search_now').addClass('fa-circle faa-burst animated');

        $.post(url_base + "/ajax/search", {"imdbid":imdbid, "title":title, "quality":quality})
        .done(function(r){
            refresh_list('#result_list', imdbid=imdbid, quality=quality)
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
            html: true,
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
        var quality = $("select#quality_profile").val()
        search_now(imdbid, title, quality);
    });

    $('i#change_quality').click(function(){
        $this = $(this);
        $this.removeClass('fa-save');
        $this.addClass('fa-circle faa-burst animated');

        quality = $this.siblings('select').val();
        imdbid = $("span#title").attr("imdbid");

        $.post(url_base + "/ajax/update_quality_profile", {"quality": quality, "imdbid": imdbid})
        .done(function(r){
            $this.addClass('fa-save');
            $this.removeClass('fa-circle faa-burst animated');
        })


    });

/* search result actions */
    $('div#status_pop_up').on('click', 'i#manual_download', function(e){
        var $this = $(this);
        var title = $("div#title span#title").text();
        var year = $("div#title span#year").text();
        var kind = $this.attr('kind');
        var guid = $this.attr('guid');
        var imdbid = $('span#title').attr('imdbid')

        console.log(title)
        console.log(year)

        $this.addClass('fa-circle faa-burst animated');

        $.post(url_base + "/ajax/manual_download", {"title": title,
                                                    "year": year,
                                                    "guid":guid,
                                                    "kind":kind
                                                    })
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

    function refresh_list(list, imdbid, quality){
        scroll_position = $(list).scrollTop();
        if(imdbid === undefined) {
            imdbid = '';
        };

        var $list = $(list)
        cls_obj = $list.prop('classList');

        var classes = ''

        $.each(cls_obj, function(k,v){
            classes = classes + v + ' '
        })


        $.post(url_base + "/ajax/refresh_list", {"list":list, 'imdbid':imdbid, "quality":quality})
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
