$(document).ready(function(){
    var url_base = $("meta[name='url_base']").attr("content");
    var notifs = JSON.parse($("meta[name='notifications']").attr("content"));

    $.each(notifs, function(index, notif){
        type = notif['type'];
        body = notif['body'];
        title = notif['title'];
        params = notif['params'];


        if(params['onclick'] != undefined){
            params['onclick'] = window[params['onclick']]
        }

        console.log(params)
        toastr[type](body, title, params);

    });
});

function update_now(){
    console.log('UPDATE NOW');
    return
    $.post(url_base + "/ajax/update_now", {"mode": "set_true"})
    .done(function(){
        window.location = url_base + "/update";
    });
};
