$(document).ready(function() {
    $('button#add').click(function(e) {
        $this = $(this);
        $this.css('background-color', '#212121');
        $this.css('color', 'white');
        $this.width($this.width());
        $this.text('• • •');

        // because we are pulling a string out of the div we need to make it an object, then have json turn it into a string
        data = $.parseJSON( $('div#hidden_data').text() );
        data = JSON.stringify(data);

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
