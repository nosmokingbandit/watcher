$(document).ready(function() {
    var url_base = $("meta[name='url_base']").attr("content");
    var directory = "";
    // set default state for pseudo checkboxes
    $("i.checkbox").each(function(){
        $this = $(this);
        if ($this.attr("value") == "True" ){
            $this.removeClass("fa-square-o");
            $this.addClass("fa-check-square");
        }
    });

    // toggle checkbox status
    $("div#content").on("click", "i.checkbox", function(){
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
            var file_list = JSON.parse(r);

            if($.isEmptyObject(file_list)){
                $("span#not_found").show();
                $("span#import").hide();
            }


            var $table = $("table#files")
            var missing_data = {}
            var $mtable = $("table#missing_data")


            $table.append("<tr><th>Import</th><th>File path</th><th>Title</th><th>IMDB ID</th><th>Resolution</th><th>Size</th>")

            $.each(file_list, function(filepath, data){
                var short_name = filepath.replace(directory, '');
                var imdbid = data["imdbid"];
                var title = data["title"];
                var resolution = data["resolution"];
                var size = parseInt(data["size"] / 1024 / 1024)
                var str_data = JSON.stringify(data);

                if(imdbid == null || resolution == null){
                    missing_data[filepath] = data
                    return true
                }

                var item = `<tr>
                                <th class="hidden data">
                                    ${str_data}
                                </th>
                                <th>
                                    <i class="fa fa-check-square checkbox" value="True"/>
                                </th>
                                <th>
                                    ${short_name}
                                </th>
                                <th>
                                    ${title}
                                </th>
                                <th>
                                    ${imdbid}
                                </th>
                                <th>
                                    ${resolution}
                                </th>
                                <th>
                                    ${size} MB
                                </th>
                            </tr>`
                $table.append(item)
            })

            if($table.find("tr").length > 1){
                $("div#review").show();
            }


            if($.isEmptyObject(missing_data) == false){
                $mtable.append("<tr><th>Import</th><th>File path</th><th>Title</th><th>IMDB ID</th><th>Resolution</th><th>Size</th>")

                $.each(missing_data, function(filepath, data){
                    var short_name = filepath.replace(directory, '');
                    var imdbid = data["imdbid"];
                    if(imdbid == null){
                        imdbid = "";
                    }
                    var title = data["title"];
                    var resolution = data["resolution"];
                    var size = parseInt(data["size"] / 1024 / 1024)
                    var str_data = JSON.stringify(data);

                    var res_select = $(`<select class="input_resolution">
                                      <option value="4K">4K</option>
                                      <option value="1080P">1080P</option>
                                      <option value="720P">720P</option>
                                      <option value="SD">SD</option>
                                  </select>`)

                    res_select.find("option").each(function(){
                        $opt = $(this);
                        if($opt.attr("value") == resolution){
                            $opt.attr("selected", "selected");
                            return true
                        };
                    });

                    res_select = res_select.prop("outerHTML");

                    var item = `<tr>
                                    <th class="hidden data">
                                        ${str_data}
                                    </th>
                                    <th>
                                        <i class="fa fa-check-square checkbox" value="True"/>
                                    </th>
                                    <th class="short_name">
                                        ${short_name}
                                    </th>
                                    <th>
                                        ${title}
                                    </th>
                                    <th>
                                        <input type="text" placeholder="tt0123456" class="input_imdbid" value="${imdbid}"/>
                                    </th>
                                    <th>
                                        ${res_select}
                                    </th>
                                    <th>
                                        ${size} MB
                                    </th>
                                </tr>`
                    $mtable.append(item)
                })
            }

            if($mtable.find("tr").length > 1){
                $("div#incomplete").show();
            }

            $("div#thinker").fadeOut();
            $("div#wait").hide();
            $("div#list_files").fadeIn();

        })
    })

    $("span#import").click(function(){
        var $rows = $("table#files tr")

        var selected = [];

        $.each($rows, function(){
            $this = $(this);
            if(is_checked($this.find("i"))){
                selected.push(JSON.parse($this.find('th.data').text()));
            }
        })

        corrected_movies = {};

        var $crows = $("table#missing_data tr");
        if($.isEmptyObject($crows) == false){
            $.each($crows, function(idx, elem){
                $elem = $(elem);
                if(is_checked($elem.find("i"))){
                    var imdbid = $elem.find("input.input_imdbid").val();
                    var resolution = $elem.find("select.input_resolution").val();
                    var path = directory + $.trim($elem.find("th.short_name").text());
                    var metadata = JSON.parse($elem.find('th.data').text());

                    metadata['imdbid'] = imdbid;
                    metadata['resolution'] = resolution;

                    corrected_movies[path] = metadata;
                }
            })
        }

        if(selected.length == 0 && $.isEmptyObject(corrected_movies) == true){
            toastr.warning("All imports disabled.");
            return false
        }

        $("div#list_files").hide();
        $("div#thinker").fadeIn();

        data = JSON.stringify(selected)
        corrected_movies = JSON.stringify(corrected_movies);

        $.post(url_base + "/ajax/submit_import", {"movie_data":data, "corrected_movies": corrected_movies})
        .done(function(r){
            results = JSON.parse(r);

            failed = results['failed']
            success = results['success']

            $results = $("div#results")

            if(failed.length > 0){
                $("div#results").prepend("<table id='failed'></ul>");
                $("div#results").prepend("<span>The following movies failed to import.</span>");

                $failed_table = $("table#failed");

                $failed_table.append(`<tr><th>File path</th><th>Error</th></tr>`);

                $.each(failed, function(idx, movie){
                    var short_name = movie['filepath'].replace(directory, '');
                    var error = movie['error'];

                    var item = `<tr>
                                    <th>
                                        ${short_name}
                                    </th>
                                    <th>
                                        ${error}
                                    </th>
                                </tr>`
                    $failed_table.append(item)
                })
            }

            if(success.length > 0){
                $("div#results").prepend("<table id='success'></ul>");
                $("div#results").prepend("<span>Successfully imported:</span>");

                $success_table = $("table#success");

                $success_table.append(`<tr><th>Title</th><th>IMDB ID</th></tr>`);
                $.each(success, function(idx, movie){
                    var title = movie['title'];
                    var year = movie['year'];
                    var imdbid = movie['imdbid'];

                    var item = `<tr>
                                    <th>
                                        ${title} (${year})
                                    </th>
                                    <th>
                                        ${imdbid}
                                    </th>
                                </tr>`
                    $success_table.append(item)
                })
            }

            $("div#thinker").fadeOut();
            $results.fadeIn();

        })

    });

    function is_checked(checkbox){
        // Turns value of checkbox "True"/"False" into js bool
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
