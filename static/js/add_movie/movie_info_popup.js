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
    $('i.checkbox').each(function(){
       if ( $(this).attr("value") == "true" ){
           $(this).removeClass('fa-square-o');
           $(this).addClass('fa-check-square-o');
       }
    });

    /* toggle check box status */
    $('i.checkbox').click(function(){
        // turn on
        if( $(this).attr("value") == "false" ){
            $(this).attr("value", "true");
            $(this).removeClass('fa-square-o');
            $(this).addClass('fa-check-square-o');
        // turn off
        } else if ( $(this).attr("value") == "true" ){
            $(this).attr("value", "false");
            $(this).removeClass('fa-check-square-o');
            $(this).addClass('fa-square-o');
        }
    });

    /* add movie action */
    $('i#button_add').click(function(e) {
        $this = $(this);
        $this.hide()

        $('iframe').fadeOut();
        $('ul#quality').fadeIn();
        $('i#button_submit').show();
        e.preventDefault();
    });


    $('i#button_submit').click(function(e){
        $this = $(this);
        $this.addClass('fa-circle faa-burst animated');

        quality_dict = {}
        // QUALITY options. This has a lot of data, so this wil get messy.
        var Quality = {},
            tmp = {};
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
            Quality[res] = dt
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

        $.post("ajax/add_wanted_movie", {"data": data})
        .done(function(r){

            response = JSON.parse(r)

            if(response['status'] == 'success'){
                swal("", response['message'], 'success');
            } else {
                swal("", response['message'], 'error');
            };

            $this.removeClass('fa-circle faa-burst animated');
            $this.hide();
            $('iframe').fadeIn();
            $('ul#quality').fadeOut();
        });

    e.preventDefault();
    });
});
