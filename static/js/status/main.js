jQuery.fn.justtext = function() {

	return $(this)	.clone()
			.children()
			.remove()
			.end()
			.text();

};


$(document).ready(function() {
    var url_base = $("meta[name='url_base']").attr("content");
    var $movielist = $('ul#movie_list');


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

    $('select#statuslist').change(function(){
        style = $("select#statuslist option:selected").val()

        $.post(url_base + "/ajax/save_single", {"cat": "UI", "key": "statuslist", "val": style})
        .done(function(r){
            if(r != 'success'){
                toastr.error("Unable to save default view. Check log for more information.");
            }
            $movielist.removeClass();
            $movielist.addClass(style);
        });
    });

    $('select#statusorder').change(function(){
        order = $("select#statusorder option:selected").val()

        sortOrder(order, $movielist, 'li')

        function sortOrder(order, $parent, children) {
            // parent must be jquery object
                $element = $parent.children(children);

            $element.sort(function(a, b) {
                var an = $(a).find('span.'+order).justtext(),
                bn = $(b).find('span.'+order).justtext();

                console.log(an)

                if (an > bn)
                    return 1;
                if (an < bn)
                    return -1;

                return 0;
            });

            $element.detach().appendTo($parent);
        }

    });


});
