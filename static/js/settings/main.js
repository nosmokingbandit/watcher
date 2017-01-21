$(document).ready(function () {
    var url_base = $("meta[name='url_base']").attr("content");
    var git_url = $("meta[name='git_url']").attr("content");

    /* Shared */

    // set default state for pseudo checkboxes
    $("i.checkbox").each(function(){
       if ( $(this).attr("value") == "true" ){
           $(this).removeClass("fa-square-o")
           $(this).addClass("fa-check-square-o");
       }
    });

    // toggle checkbox status
    $("div#content").on("click", "i.checkbox", function(){
        // turn on
        if( $(this).attr("value") == "false" ){
            $(this).attr("value", "true");
            $(this).removeClass("fa-square-o")
            $(this).addClass("fa-check-square-o");
        // turn off
        } else if ( $(this).attr("value") == "true" ){
            $(this).attr("value", "false");
            $(this).removeClass("fa-check-square-o");
            $(this).addClass("fa-square-o")
        }
    });

    /* Server */

    // Generate new api key
    $("div.server i#generate_new_key").click(function(){
        var key = new_api_key(32);
        $("input#apikey").val(key);
    })

    new_api_key = function(length) {
        var text = "";
        var possible = "abcdef0123456789";
        for(var i = 0; i < length; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }

    // shutdown & restart
    $("div.server span#restart").click(function(){
        swal({
            title: "Restart Watcher?",
            text: "",
            type: "",
            showCancelButton: true,
            imageUrl: '',
            confirmButtonColor: "#4CAF50",
            confirmButtonText: "Restart",
            closeOnConfirm: true
        }, function(){
            window.location = url_base + "/restart";
        });
    });

    $("div.server span#shutdown").click(function(){
        swal({
            title: "Shut Down Watcher?",
            text: "",
            type: "",
            showCancelButton: true,
            confirmButtonColor: "#4CAF50",
            confirmButtonText: "Shut Down",
            closeOnConfirm: true
        }, function(){
            window.location = url_base + "/shutdown";
        });
    });

    // check for updates
    $("div.server span#update_check").click(function(){
        $this = $(this);
        $i = $this.find(":first");

        $i.removeClass("fa-arrow-circle-up");
        $i.addClass("fa-circle faa-burst animated");

        $.post(url_base + "/ajax/update_check", {})
        .done(function(r){

            response = JSON.parse(r);
            if(response['status'] == 'current'){
                toastr.info("No updates available.");
            } else if(response['status'] == 'error'){
                toastr.warning(response['error']);
            } else if(response["status"] == "behind"){

                if(response["behind_count"] == 1){
                    title = response["behind_count"] + " Update Available";
                } else {
                    title = response["behind_count"] + " Updates Available";
                };

                compare = git_url + "/compare/" + response["local_hash"] + "..." + response["new_hash"]

                body = "Click <a href='update_now'><u>here</u></a> to update now. <br/> Click <a href=" + compare + " target=_blank><u>here</u></a> to view changes."


                toastr.info(body, title, {closeButton:true,
                                          timeOut: 0,
                                          extendedTimeOut: 0,
                                          tapToDismiss: 0
                                          });

            }
        $i.addClass("fa-arrow-circle-up");
        $i.removeClass("fa-circle faa-burst animated");

        })
    });

    // Install updates
    function update_now(){
        $.post(url_base + "/ajax/update_now", {"mode": "set_true"})
        .done(function(){
            window.location = url_base + "/update";
        });
    };

    /* Providers */

    // Add new rows
    $("div.providers i#add_row").click(function (){
        var row = "<li class='newznab_indexer'>\n<i class='fa fa-square-o newznab_check checkbox' value='false'></i>\n<input class='newznab_url' placeholder=' http://indexer.url' type='text'>\n<input class='newznab_api' placeholder=' Api Key' type='text'><i class='newznab_clear fa fa-trash-o'></i><i class='newznab_test fa fa-plug'/>\n</li>"

        $("ul#newznab_list li:nth-last-child(2)").after(row);
    });

    // clear row
    $("div.providers ul#newznab_list").on("click", "i.newznab_clear", function(){
        $li = $(this).parent();
        $li.find('input').each(function(){
            $(this).val("");
        });
    });

    // test newznab connection
    $("div.providers ul#newznab_list").on("click", "i.newznab_test", function(){
        $this = $(this);
        var name = $this.attr('name');

        $this.removeClass("fa-plug");
        $this.addClass("fa-circle faa-burst animated");

        var url = "";
        var api = "";

        $li = $(this).parent();
        $li.find('input.newznab_url').each(function(){
            url = $(this).val();
        });

        $li.find('input.newznab_api').each(function(){
            api = $(this).val();
        });

        $.post(url_base + "/ajax/newznab_test", {"indexer": url, "apikey": api})
        .done(function(r){
            response = JSON.parse(r);
            if(response["code"] == 10061){
                toastr.error(response["description"]);
            } else if(response["code"] == 100){
                toastr.warning(response["description"]);
            } else if(response["code"] == 200){
                toastr.success("Connection successful.");
            }

        $this.addClass("fa-plug");
        $this.removeClass("fa-circle faa-burst animated");

        })

    });


    /* Downloader */

    // set default state for radios and downloader options
    $("div.downloader i.radio").each(function(){
       if ( $(this).attr("value") == "true" ){
           u = ("ul#" + $(this).attr("tog"));
           $(u).show()
           $(this).removeClass("fa-circle-o")
           $(this).addClass("fa-circle");
       }
    });

    // toggle downloader slide-downs
    $("div.downloader i.radio").click(function(){
        $this = $(this);
        // turn on
        if( $this.attr("value") == "false" ){
            $this.attr("value", "true");
            $this.removeClass("fa-circle-o")
            $this.addClass("fa-circle");
        // and turn off the other ones
            var tog = $this.attr("tog");
            $("ul#"+tog).stop().slideDown();
            $("ul#downloader ul").not($("#"+tog)).stop().slideUp()
            $("i.radio[tog!="+tog+"]").attr("value", "false").removeClass("fa-circle").addClass("fa-circle-o");
        }
    });

    // test downloader connection
    $("div.downloader span.test_connection").click(function(){
        $this = $(this)
        $thisi = $this.children(":first");

        $thisi.removeClass("fa-plug");
        $thisi.addClass("fa-circle faa-burst animated");

        var mode = $this.attr("mode");
        var inputs = "ul#" + mode + " li input";

        // Gets entered info, even if not saved
        var data = {}
        $(inputs).each(function(){
            data[$(this).attr("id")] = $(this).val()
        });

        data = JSON.stringify(data);

        $.post(url_base + "/ajax/test_downloader_connection", {
            "mode": mode,
            "data": data
        })
        .done(function(r){
            var response = JSON.parse(r);
            $thisi.addClass("fa-plug");
            $thisi.removeClass("fa-circle faa-burst animated");

            if(response["status"] == "false"){
                toastr.error(response["message"]);
            } else {
                toastr.success(response["message"]);
            }
        })
    });

    /* Quality */

    // set up sortable
    $(function () {
        $("ul.sortable").sortable();
        $("ul.sortable").disableSelection();
    });

    $("div.quality ul.sortable").sortable({
        cancel: "span.not_sortable"
    });

    // set order for sortable items
    $("div.quality ul#resolution li").each(function () {
        $(this).siblings().eq($(this).attr("sort")).after($(this));
    });
    $("div.quality ul#sources li").each(function () {
        $(this).siblings().eq($(this).attr("sort")).after($(this));
    });

    /* Logs */

    // Open log file
    $("span#view_log").click(function(){
        $log_display = $("pre#log_display");
        $log_display.hide();
        logfile = $("select#log_file").val();

        $.post(url_base + "/ajax/get_log_text", {'logfile': logfile})
        .done(function(r){
            $log_display.text(r);
            $log_display.show();
        });

    });

    // Download log file
    $("span#download_log").click(function(){
        logfile = $("select#log_file").val();
        window.open(url_base + '/logs/' + logfile)
    });

});
