$(document).ready(function () {
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

    /* add new newznab row */
    $('i#add_row').click(function (e){

        add_newznab_row();

        e.preventDefault();
    });

    function add_newznab_row(){
        var row = "<li class='newznab_indexer'>\n<i class='fa fa-square-o newznab_check checkbox' value='false'></i>\n<input class='newznab_url' placeholder=' URL' type='text'>\n<input class='newznab_api' placeholder=' Api Key' type='text'>\n</li>"

        $('ul#newznab_list li:nth-last-child(2)').after(row);
    }

    /* set default state for pseudo checkboxes */
    $('i.checkbox').each(function(){
       if ( $(this).attr("value") == "true" ){
           $(this).removeClass('fa-square-o')
           $(this).addClass('fa-check-square-o');
       }
    });

    /* toggle checkbox status */
    $('div#content').on('click', 'i.checkbox', function(){
        // turn on
        if( $(this).attr("value") == "false" ){
            $(this).attr("value", "true");
            $(this).removeClass('fa-square-o')
            $(this).addClass('fa-check-square-o');
        // turn off
        } else if ( $(this).attr("value") == "true" ){
            $(this).attr("value", "false");
            $(this).removeClass('fa-check-square-o');
            $(this).addClass('fa-square-o')
        }
    });

    /* set default state for pseudo radios and their slide downs*/
    $('i.radio').each(function(){
       if ( $(this).attr("value") == "true" ){
           u = ("ul#" + $(this).attr("tog"));
           $(u).show()
           $(this).removeClass('fa-circle-o')
           $(this).addClass('fa-circle');
       }
    });


    /* toggle downloader slide downs */
    $('i.radio').click(function(){
        // turn on
        if( $(this).attr("value") == "false" ){
            $(this).attr("value", "true");
            $(this).removeClass('fa-circle-o')
            $(this).addClass('fa-circle');

            // and turn off the other one
            var tog = $(this).attr('tog');
            $('ul#'+tog).stop().slideDown();
            $('ul#downloader ul').not($('#'+tog)).stop().slideUp()
            $("i.radio[tog!='"+tog+"']").attr("value", "false").removeClass('fa-circle').addClass('fa-circle-o');

        // turn off
        } else if ( $(this).attr("value") == "true" ){
            $(this).attr("value", "false");
            $(this).removeClass('fa-circle');
            $(this).addClass('fa-cricle-o');
            var tog = $(this).attr('tog');
            $('ul#'+tog).stop().slideUp();
        }
    });

    /* test connection post */
    $('span.test_connection').click(function(){
        $this = $(this)
        $thisi = $this.children(':first');

        $thisi.removeClass('fa-plug');
        $thisi.addClass('fa-circle faa-burst animated');

        var mode = $this.attr('mode');
        var cont = "ul#" + mode + " li input";

        // Gets entered info, even if not saved
        var data = {}
        $(cont).each(function(){
            data[$(this).attr("id")] = $(this).val()
        });

        data = JSON.stringify(data);

        $.post("/test_downloader_connection", {
            "mode": mode,
            "data": data
        })
        .done(function(r){
            var response = JSON.parse(r);
            $thisi.addClass('fa-plug');
            $thisi.removeClass('fa-circle faa-burst animated');

            if(response['status'] == 'false'){
                swal("Error", response['message'], 'warning');
            } else {
                swal("Connected!", response['message'], 'success');
            }
        })
    });

    /* Generate new api key */
    $('i#generate_new_key').click(function(){
        var key = new_api_key(32);
        $('input#apikey').val(key);
    })

    new_api_key = function(length) {
        var text = "";
        var possible = "abcdef0123456789";
        for(var i = 0; i < length; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }

    /* shutdown / restart */

    $('span#restart').click(function(){
        swal({
            title: "Restart Watcher?",
            text: "",
            type: "info",
            showCancelButton: true,
            confirmButtonColor: "#F44336",
            confirmButtonText: "Restart",
            closeOnConfirm: true
        }, function(){
            window.location = "/restart";
        });
    });

    $('span#shutdown').click(function(){
        swal({
            title: "Shut Down Watcher?",
            text: "",
            type: "info",
            showCancelButton: true,
            confirmButtonColor: "#F44336",
            confirmButtonText: "Shut Down",
            closeOnConfirm: true
        }, function(){
            window.location = "/shutdown";
        });
    });
});
