$(document).ready(function () {
    var url_base = $("meta[name='url_base']").attr("content");

    $("span#save").click(function(e){
        if(verify_data() == false){
            return;
        }

        $this = $(this);
        $thisi = $this.children(':first');

        cat = $this.attr('cat');

        if(cat == 'server'){
            data = server();
        } else if(cat == 'search'){
            data = search();
        } else if(cat == 'quality'){
            data = quality()
        } else if(cat == 'providers'){
            data = providers()
        } else if(cat == 'downloader'){
            data = downloader()
        }else if(cat == 'postprocessing') {
            data = postprocessing()
        }

        if(data == false){
            return
        }

        post_data = JSON.stringify(data);

        $thisi.removeClass('fa-save')
        $thisi.addClass('fa-circle faa-burst animated');

        $.post(url_base + "/ajax/save_settings", {
            "data": post_data
        })

        .done(function(r) {
            if(r == 'failed'){
                swal("Error", "Unable to save settings. Check log for more information.", "error")
            }
            else if(r == 'success'){
                swal("Settings Saved", "", "success")
            }

            $thisi.removeClass('fa-circle faa-burst animated');
            $thisi.addClass('fa-save');
        });

        e.preventDefault();
    });

    function server(){
        var data = {};
        var server = {};
        var blanks = false;
        $("#server i.checkbox").each(function(){
            server[$(this).attr("id")] = $(this).attr("value");
        });
        $("#server :input").each(function(){
            if($(this).attr('id') == 'theme'){
                
            }
            else if($(this).val() == ''){
                blanks = true;
                highlight($(this));
            }
            server[$(this).attr("id")] = $(this).val();
        });

        if(blanks == true){
            return false;
        };

        data['Server'] = server

        return data
    }

    function search(){
        var data = {};
        var search = {};
        var blanks = false;
        $("ul#search i.checkbox").each(function(){
            search[$(this).attr("id")] = $(this).attr("value");
        })
        $("ul#search :input").each(function(){
            if($(this).val() == ''){
                blanks = true;
                highlight($(this));
            }
            search[$(this).attr("id")] = $(this).val();
        });
        if(blanks == true){
            return false;
        };

        data["Search"] = search;
        return data
    }

    function quality(){
        var data = {};
        var quality = {};
        var tmp = {};
        var blanks = false;

        var q_list = [];
        $("ul#resolution i.checkbox").each(function(){
            q_list.push( $(this).attr("id") );
        });

        // enabled resolutions
        $("ul#resolution i.checkbox").each(function(){
            tmp[$(this).attr("id")] = $(this).attr("value");
        }); // ## TODO clean this up

        // order of resolutions
        var arr = $("ul#resolution").sortable("toArray");
        arr.shift();
        $.each(arr, function(i, v){
            tmp[v] = i;
        });
        // min/max sizes
        $("#resolution_size :input").each(function(){
            if($(this).val() == ''){
                blanks = true;
                highlight($(this));
            }
            tmp[$(this).attr("id")] = $(this).val();
        });

        if(blanks == true){
            return false;
        };

        $.each(q_list, function(i, res){
            var enabled = res,
                priority = res + "priority",
                min = res + "min",
                max = res + "max";
            var dt = [tmp[enabled], tmp[priority], tmp[min], tmp[max]]
            quality[res] = [tmp[enabled], tmp[priority], tmp[min], tmp[max]].join(',');
        });

        data["Quality"] = quality;

        // FILTERS options.
        var filters = {};
        $("ul#filters li input").each(function(){
            var val = $(this).val().split(", ").join(",");
            filters[$(this).attr("id")] = val;
        });
        data["Filters"] = filters;

        return data
    }

    function providers(){
        // The order of these tend to get jumbled. I think it sorts alphabetically, but
        // I haven't put much effort into it yet because it really doesn't affect usage.
        var data = {};
        var indexers = {};
        var ind = 1;

        $("#newznab_list li").each(function(){
            if ($(this).attr("class") == "newznab_indexer"){
                var check = $(this).children("i.newznab_check").attr('value');
                var url = $(this).children("input.newznab_url").val();
                var api = $(this).children("input.newznab_api").val();

                // check if one field is blank and both are not blank
                if ( (url == "" || api == "") && (url + api !=="") ){
                    swal("", "Please complete or clear out incomplete providers.", "warning");
                    indexers = {}
                    return false;
                }

                // but ignore it if both are blank
                else if (url + api !=="") {
                    indexers[ind] = [url, api, check].toString().toLowerCase();
                    ind++;
                }
            }
        });
        data["Indexers"] = indexers;

        return data
    }

    function downloader(){
        var data = {}
        var sabnzbd = {};
        sabnzbd["sabenabled"] = $("i#sabenabled").attr("value");
        $("ul#sabnzbd li input").each(function(){
            sabnzbd[$(this).attr("id")] = $(this).val()
        });
        $("ul#sabnzbd li select").each(function(){
            sabnzbd[$(this).attr("id")] = $(this).val()
        });
        data["Sabnzbd"] = sabnzbd;

        var nzbget = {};
        nzbget["nzbgenabled"] = $("i#nzbgenabled").attr("value");
        $("ul#nzbget li i.checkbox").each(function(){
            nzbget[$(this).attr("id")] = $(this).attr("value");
        });
        $("ul#nzbget li input").not("[type=button]").each(function(){
            nzbget[$(this).attr("id")] = $(this).val();
        });
        $("ul#nzbget li select").each(function(){
            nzbget[$(this).attr("id")] = $(this).val()
        });
        data["NzbGet"] = nzbget;

        return data
    }

    function postprocessing(){
        var data = {}
        var postprocessing = {}
        $("ul#postprocessing li i.checkbox").each(function(){
            postprocessing[$(this).attr("id")] = $(this).attr("value");
        });
        $("ul#postprocessing li input").not("[type=button]").each(function(){
            postprocessing[$(this).attr("id")] = $(this).val();
        });

        data["Postprocessing"] = postprocessing;

        return data
    }

    function verify_data(){

        //check if only one downloader is active:
        var enabled = 0
        $('ul#downloader > li > i.checkbox').each(function(){
            if($(this).attr('value') == 'true'){
                enabled++;
            }
        });

        if(enabled > 1){
            swal("", "Please enable only one downloader.", "warning");
            return false
        }
        return true
    }

    function highlight(element){
        orig_bg = element.css('background-color');
        element.css('background-color', '#f4693b');
        element.delay(500).animate({'background-color': orig_bg}, 1000);
    }

});
