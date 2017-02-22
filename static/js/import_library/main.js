$(document).ready(function() {
    var url_base = $("meta[name='url_base']").attr("content");
    var directory = "";
    var $content = $("div#content");
    // set default state for pseudo checkboxes
    $("i.checkbox").each(function(){
        $this = $(this);
        if ($this.attr("value") == "True" ){
            $this.removeClass("fa-square-o");
            $this.addClass("fa-check-square");
        }
    });

    // toggle checkbox status
    $content.on("click", "i.checkbox", function(){
        $this = $(this);
        // turn on
        if( $this.attr("value") == "False" ){
            $this.attr("value", "True");
            $this.removeClass("fa-square-o");
            $this.addClass("fa-check-square");
        // turn off
        } else if ($this.attr("value") == "True" ){
            $this.attr("value", "False");
            $this.removeClass("fa-check-square");
            $this.addClass("fa-square-o");
        }
    });

    // file browser
    $file_list = $("ul#file_list");

    $current_dir = $("div#current_dir")

    $("div#browse").click(function(){
        $("div#browser").show();
        $("div#overlay").fadeIn();
    });

    $("i#close_browser").click(function(){
        $("div#browser").hide();
        $("div#overlay").fadeOut();
    });

    $("i#select_dir").click(function(){
        $("input#directory").val($current_dir.text());
        $("div#browser").hide();
        $("div#overlay").fadeOut();
    });

    $file_list.on("click", "li", function(){
        $this = $(this)
        path = $this.text()
        $.post(url_base+'/ajax/list_files', {"current_dir": $current_dir.text(),
                                          "move_dir": path})
        .done(function(r){
            response = JSON.parse(r);

            if(response['error']){
                toastr.warning(response['error'])
            } else {
                $current_dir.text(response['new_path'])
                $file_list.html(response['html']);
            }
        });
    });




    // submit directory information
    $("span#start_scan").click(function(){
        directory = $("input#directory").val();
        if(directory == ""){
            highlight($("input#directory"));
            return false;
        }

        var minsize = $("input#minsize").val()
        if(minsize == ""){
            highlight($("input#minsize"));
            return false;
        } else {
            minsize = parseInt(minsize);
        }

        var recursive = is_checked($("i#recursive"))

        $("div#directory_info").hide();
        $("div#thinker").fadeIn();
        $("div#wait").fadeIn();

        $.post(url_base + "/ajax/scan_library", {"directory": directory,
                                                 "minsize": minsize,
                                                 "recursive": recursive})
        .done(function(r){
            $content.html(r);
            $("div#thinker").fadeOut();
            $("div#wait").hide();
            $("div#list_files").fadeIn();

        })
    });

    $content.on("click", "span#import", function(){

        var movie_data = [];

        var $rows = $("div#review table.files tr")
        $.each($rows, function(){
            $this = $(this);
            if(is_checked($this.find("i"))){
                metadata = JSON.parse($this.find('td.data').text());
                source = $this.find("select.input_resolution").val();
                metadata['resolution'] = source;
                metadata['filepath'] = directory + $.trim($this.find("td.short_name").text());
                movie_data.push(metadata);
            }
        })

        corrected_movies = [];

        var $crows = $("div#incomplete table.files tr").slice(1);
        if($.isEmptyObject($crows) == false){
            $.each($crows, function(idx, elem){
                $elem = $(elem);
                if(is_checked($elem.find("i"))){
                    var imdbid = $elem.find("input.input_imdbid").val();
                    var resolution = $elem.find("select.input_resolution").val();
                    var metadata = JSON.parse($elem.find('td.data').text());

                    if($.trim(imdbid) == ''){
                        highlight($elem.find("input.input_imdbid"))
                        return false;
                    }

                    metadata['imdbid'] = imdbid;
                    metadata['resolution'] = resolution;
                    metadata['filepath'] = directory + $.trim($elem.find("td.short_name").text());
                    corrected_movies.push(metadata);
                }
            })
        }

        if(movie_data.length == 0 && corrected_movies.length == 0){
            toastr.warning("All imports disabled.");
            return false
        }

        $("div#list_files").hide();
        $("div#thinker").fadeIn();

        movie_data = JSON.stringify(movie_data)
        corrected_movies = JSON.stringify(corrected_movies);

        $.post(url_base + "/ajax/submit_import", {"movie_data":movie_data, "corrected_movies": corrected_movies})
        .done(function(r){
            $content.html(r)

            $("div#thinker").fadeOut();
            $("div#results").fadeIn();

        })

    });

    function is_checked(checkbox){
        // Turns value of checkbox "True"/"False" into bool
        // checkbox: object jquery object of checkbox <i>
        return (checkbox.attr("value") == "True")
    }

    function highlight(element){
        // Highlights empty or invalid inputs
        // element: object JQ object of input to highlight
        orig_bg = element.css("background-color");
        element.css("background-color", "#f4693b");
        element.delay(500).animate({"background-color": orig_bg}, 1000);
    }
})
