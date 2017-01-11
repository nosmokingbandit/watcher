jQuery.fn.justtext = function() {

	return $(this)	.clone()
			.children()
			.remove()
			.end()
			.text();
};

function read_cookie()
{
   var dcookie = document.cookie;
   cookie_obj = {};
   cookiearray = dcookie.split("; ");

   // Now take key value pair out of this array
   for(var i=0; i<cookiearray.length; i++){
      key = cookiearray[i].split("=")[0];
      value = cookiearray[i].split("=")[1];
      cookie_obj[key] = value
   }
   return cookie_obj
}

function sortOrder(order, $parent, children) {
	// parent must be jquery object
		$element = $parent.children(children);

	$element.sort(function(a, b) {
		var an = $(a).find("span."+order).justtext(),
		bn = $(b).find("span."+order).justtext();

		if (an > bn)
			return 1;
		if (an < bn)
			return -1;

		return 0;
	});

	$element.detach().appendTo($parent);
}

$(document).ready(function() {
    var url_base = $("meta[name='url_base']").attr("content");
    var $movielist = $("ul#movie_list");
	var $select_list_style = $("select#list_style")
	var $select_list_sort = $("select#list_sort")
	var cookie = read_cookie();

	/* set up list style from cookies */
	style = cookie["list_style"] || "posters";
	$movielist.removeClass();
	$movielist.addClass(style);

	$select_list_style.find("option").each(function(){
		$this = $(this);
		if($this.val() == cookie["list_style"]){
			$this.prop("selected", true);
		}
	});

	/* sort order */
	order = cookie["list_sort"] || "title";
	sortOrder(order, $movielist, "li");

	$select_list_sort.find("option").each(function(){
		$this = $(this);
		if($this.val() == order){
			$this.prop("selected", true)
		}
	});


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

	/* Set cookies for list style and sort */

    $select_list_style.change(function(){
        style = $select_list_style.find("option:selected").val()

		document.cookie = "list_style=" + style

        $movielist.removeClass();
        $movielist.addClass(style);
    });

    $select_list_sort.change(function(){
        order = $select_list_sort.find("option:selected").val()

		document.cookie = "list_sort=" + order

        sortOrder(order, $movielist, "li")

    });


});
