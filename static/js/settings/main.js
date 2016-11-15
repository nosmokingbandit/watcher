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

        var row = "<li class='newznab_indexer'>\n<i class='newznab_check material-icons toggle'value='false'>check_box</i>\n<input class='newznab_url' placeholder=' URL' type='text'>\n<input class='newznab_api' placeholder=' Api Key' type='text'>\n</li>"

        $('ul#newznab_list li:nth-last-child(2)').after(row);

        e.preventDefault();
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


    /* set default state for pseudo radios */
    $('i.radio').each(function(){
       if ( $(this).attr("value") == "true" ){
           u = ("ul#" + $(this).attr("tog"));
           $(u).show()
           $(this).text('radio_button_checked');
       }
    });


    /* toggle downloader slide downs */
    $('i.radio').click(function(){
        // turn on
        if( $(this).attr("value") == "false" ){
            $(this).attr("value", "true");
            $(this).text('radio_button_checked');

            var tog = $(this).attr('tog');
            $('ul#'+tog).stop().slideDown();
            $('ul#downloader ul').not($('#'+tog)).stop().slideUp()
            $("i.radio[tog!='"+tog+"']").attr("value", "false").text('radio_button_unchecked');

        // turn off
        } else if ( $(this).attr("value") == "true" ){
            $(this).attr("value", "false");
            $(this).text('radio_button_unchecked');
            var tog = $(this).attr('tog');
            $('ul#'+tog).stop().slideUp();
        }
    });

    /* test connection post */
    $('button.test_connection').click(function(){
        var mode = $(this).attr('mode');
        var cont = "ul#" + mode + " li input";

        $this = $(this);
        $this.css('background-color', '#212121');
        $this.css('color', 'white');
        $this.width($this.width());
        $this.text('• • •');

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
            alert(r)
            $this.css('background-color', 'white');
            $this.css('color', '#212121');
            $this.text('Test Connection');
        })
    });

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

    // shutdown/restart buttons

    $('button#restart').click(function(){
        console.log('restarting');
        if (confirm('Restart Watcher?')){
            window.location = "/restart";
        }
    });

    $('button#shutdown').click(function(){
        console.log('shutdown');
        if (confirm('Shut Down Watcher?')){
            window.location = "/shutdown";
        }
    });
});
