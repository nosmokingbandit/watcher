$(document).ready(function () {

    $("span#save").click(function(e){
        if(verify_data() == false){
            return;
        }

        $this = $(this);
        $thisi = $this.children(':first');
        $thisi.removeClass('fa-save')
        $thisi.addClass('fa-circle faa-burst animated');

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

        post_data = JSON.stringify(data);

        $.post("/save_settings", {
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
        var data = {}
        var server = {}
        $("#server i.checkbox").each(function(){
            server[$(this).attr("id")] = $(this).attr("value");
        });
        $("#server :input").each(function(){
            server[$(this).attr("id")] = $(this).val();
        });

        data['Server'] = server

        return data
    }

    function search(){
        var data = {};
        var search = {};
        $("ul#search i.checkbox").each(function(){
            search[$(this).attr("id")] = $(this).attr("value");
        })
        $("ul#search :input").each(function(){
            search[$(this).attr("id")] = $(this).val();
        });
        data["Search"] = search;

        return data
    }

    function quality(){
        var data = {}
        var quality = {}
        var tmp = {}

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
        var indexer = {};
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
                    return
                }
                // but ignore it if both are blank
                else if (url + api !=="") {
                    var data = [url, api, check].toString().toLowerCase();
                    indexers[ind] = data;
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

});
