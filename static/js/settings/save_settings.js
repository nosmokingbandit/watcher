$(document).ready(function () {

/* grab all settings and write them to the config writer */
    $("button#save_settings").click(function(e){

        //check if only one downloader is active:
        var enabled = 0
        $('ul#downloader > li > i.toggle').each(function(){
            console.log($(this).attr('value'));
            if($(this).attr('value') == 'true'){
                enabled++;
            }
        });

        if(enabled > 1){
            alert('Please enable only one downloader.')
            return
        }

        $this = $(this);
        $this.css('background-color', '#212121');
        $this.css('color', 'white');
        $this.width($this.width());
        $this.text('- - -');

        var post_list = {};

        // SEARCH options
        var Search = {};
        $("ul#search i.toggle").each(function(){
            Search[$(this).attr("id")] = $(this).attr("value");
        })
        $("ul#search :input").each(function(){
            Search[$(this).attr("id")] = $(this).val();
        });
        post_list["Search"] = Search;

        // INDEXER options
        // The order of these tend to get jumbled. I think it sorts alphabetically, but I haven't put much effort into it yet because it really doesn't affect usage.
        var Indexers = {};
        var ind = 1;

        $("#newznab_list li").each(function(){
            if ($(this).attr("class") == "newznab_indexer"){
                var check = $(this).children("i.newznab_check").attr('value');
                var url = $(this).children("input.newznab_url").val();
                var api = $(this).children("input.newznab_api").val();

                // check if one field is blank and both are not blank
                if ( (url == "" || api == "") && (url + api !=="") ){
                    alert("Please complete or clear out incomplete providers.");
                    Indexers = {}
                    return
                }
                // but ignore it if both are blank
                else if (url + api !=="") {
                    var data = [url, api, check].toString().toLowerCase();
                    Indexers[ind] = data;
                    ind++;
                }
            }
        });
        post_list["Indexers"] = Indexers;

        // QUALITY options. This has a lot of data, so this wil get messy.
        var Quality = {},
            tmp = {};

        var q_list = []
        $("ul#resolution i.toggle").each(function(){
            q_list.push( $(this).attr("id") );
        });

        // enabled resolutions
        $("ul#resolution i.toggle").each(function(){
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

        $.each(q_list, function(i, v){
            var enabled = v,
                priority = v + "priority",
                min = v + "min",
                max = v + "max";
            var dt = [tmp[enabled], tmp[priority], tmp[min], tmp[max]]
            Quality[v] = dt.join();
        });

        post_list["Quality"] = Quality;

        // FILTERS options.
        var Filters = {};
        $("ul#filters li input").each(function(){
            var val = $(this).val().split(", ").join(",");
            Filters[$(this).attr("id")] = val;
        });
        post_list["Filters"] = Filters;

        // DOWNLOADER options.
        var Sabnzbd = {};
        Sabnzbd["sabenabled"] = $("i#sabenabled").attr("value");
        $("ul#sabnzbd li input").each(function(){
            Sabnzbd[$(this).attr("id")] = $(this).val()
        });
        $("ul#sabnzbd li select").each(function(){
            Sabnzbd[$(this).attr("id")] = $(this).val()
        });
        post_list["Sabnzbd"] = Sabnzbd;

        var NzbGet = {};
        NzbGet["nzbgenabled"] = $("i#nzbgenabled").attr("value");
        $("ul#nzbget li i.toggle").each(function(){
            NzbGet[$(this).attr("id")] = $(this).attr("value");
        });
        $("ul#nzbget li input").not("[type=button]").each(function(){
            NzbGet[$(this).attr("id")] = $(this).val();
        });
        $("ul#nzbget li select").each(function(){
            NzbGet[$(this).attr("id")] = $(this).val()
        });
        post_list["NzbGet"] = NzbGet;


        // POSTPROCESSING options
        var Postprocessing = {}
        $("ul#postprocessing li i.toggle").each(function(){
            Postprocessing[$(this).attr("id")] = $(this).attr("value");
        });
        $("ul#postprocessing li input").not("[type=button]").each(function(){
            Postprocessing[$(this).attr("id")] = $(this).val();
        });

        post_list["Postprocessing"] = Postprocessing;

        // SERVER options
        var Server = {}
        $("#server i.toggle").each(function(){
            Server[$(this).attr("id")] = $(this).attr("value");
        });
        $("#server :input").each(function(){
            Server[$(this).attr("id")] = $(this).val();
        });

        post_list["Server"] = Server;

        // make it pretty.
        var post_data = JSON.stringify(post_list)

        // Whew, finally got all of the data. That wasn"t so bad.

        $.post("/save_settings", {
            "data": post_data
        })

        .done(function(r) {
            if(r == 'failed'){
                alert('Unable to save settings. Check log for more information.')
            }
            else if(r == 'success'){
                alert('Settings saved.')
            }
            else if(r == 'purgefail'){
                alert('Search criteria has changed, but old search results couldn not be removed. Check log for more information.')
            }
            else {
                var search_confirm = confirm("Search criteria has changed and search must run for all movies to update results. The next automatic update is scheduled for "+r+". Would you like to search all movies immediately?")

            }

            if(search_confirm == true){
                $.post("/search_all", {})
            }

            $this.css('background-color', 'white');
            $this.css('color', '#212121');
            $this.text('Save Settings');
        });

        e.preventDefault();
    });
});
