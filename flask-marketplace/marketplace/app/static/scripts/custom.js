$(document).ready(function () {
    $(document).on('click', '.options.btn', function () {
        if ($(this).next('.popup').hasClass('visible')) {
            $(this).popup('hide all');
            $(this).removeClass('active');
        } else {
            $(this).addClass('active');
            $(this).popup({
                inline: true,
                position: 'bottom right',
                on: 'click',
            }).popup("show");
        }
    });
});

$(document).ready(function () {
    $('#trigger1').click(function () {
        $('#overlay').fadeIn(300);
    });
    $('#close').click(function () {
        $('.fullscreen.modal').fadeOut(300);
    });
});
$(document).ready(function () {
    $(document).on('click', '.floating.action', function () {
        $('.ui.sidebar')
            .sidebar('toggle')
        ;
    });
});
function refreshImages(){
    $(document).ready(function ( ) {
        let images = $('.post-image');
        let ids = [];
        $(images).each(function (){
            let content = $(this).attr('data-content');
            if (! ids.includes(content)){
                ids.push(content);
            }
        });
        for (let i=0; i<ids.length; i++){
            let content = ids[i];
            let patch = $('.post-image[data-content='+content+']');
            $(patch).each(function (){
                let sizes = $(this).attr('data-size');
                sizes = JSON.parse(sizes);
                let w = sizes[0];
                let h = sizes[1];
                let cw = $(this).width();
                let ch = Math.floor(h*cw/w);
                $(this).css('height', ch);
            })
        }
    });
}
$(document).ready(function () {
    refreshImages();
});