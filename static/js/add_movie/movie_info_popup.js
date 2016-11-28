$(document).ready(function() {
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

    /* add movie action */
    $('i#button_add').click(function(e) {
        $this = $(this);
        $this.hide()


        $('iframe').slideUp();
        $('ul#quality').slideDown();
        $('i#button_submit').show()
        e.preventDefault();
    });


    $('i#button_submit').click(function(e){
        quality_dict = {}
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

        quality_dict["Quality"] = Quality;

        // FILTERS options.
        var Filters = {};
        $("ul#filters li input").each(function(){
            var val = $(this).val().split(", ").join(",");
            Filters[$(this).attr("id")] = val;
        });
        quality_dict["Filters"] = Filters;

        quality = JSON.stringify(quality_dict);

        // because we are pulling a string out of the div we need to make it an object, then have json turn it into a string
        data = $.parseJSON( $('div#hidden_data').text() );
        data['quality'] = quality;
        data = JSON.stringify(data);

        console.log(data);

        $.post("/add_wanted_movie", {"data": data})
        .done(function(r){
            alert(r);
            $this.css('background-color', 'white');
            $this.css('color', '#212121');
            $this.text('Add');

        });

    e.preventDefault();
    });
});
