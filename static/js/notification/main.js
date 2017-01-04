$(document).ready(function(){
    var url_base = $("meta[name='url_base']").attr("content");
    window.url_base = url_base;
    var notifs = JSON.parse($("meta[name='notifications']").attr("content"));

    $.each(notifs, function(index, notif){
        type = notif['type'];
        body = notif['body'];
        title = notif['title'];
        params = notif['params'];

        if(params['onclick'] != undefined){
            params['onclick'] = window[params['onclick']]
        }

        params['onCloseClick'] = remove_notif;
        params['index'] = index;

        toastr[type](body, title, params);

    });
});

function update_now(){
    $.post(url_base + "/ajax/update_now", {"mode": "set_true"})
    .done(function(){
        window.location = url_base + "/update";
    });
};


/* sends post to remove notification from list */
function remove_notif(){
    index = this['index']
    $.post(window.url_base + "/ajax/notification_remove", {
        "index": index
    })
}
