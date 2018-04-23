var $ = jQuery // WTF!

jQuery(function() {
    jQuery(window).scroll(function() {
        jQuery(this).scrollTop() > 200 ? jQuery("#zan-gotop").css({
            bottom: "20px"
        }) : jQuery("#zan-gotop").css({
            bottom: "-40px"
        });
    });

    jQuery("#zan-gotop").click(function() {
        return jQuery("body,html").animate({
            scrollTop: 0
        }, 500), !1
    });
})

function load_articles() {
    var links = jQuery('.panel-heading a[data-lazyload]')
    for (var i = 0; i < links.length; ++i) {
        var $a = jQuery(links[i])
        load_article($a.attr('data-lazyload'), $a.closest('div.panel'))
    }
}

function load_article(url, $panel) {
    console.log(url, $panel)    
    jQuery.ajax({
        type: 'GET',
        url: url + '?data=link'
    }).done(function (res) {
        $panel.find('.panel-body').html(res)
    })
}

function load_search_thumb() {
    function resize_detail(id) {
        $('#detail-'+ id).attr('class', 'col-md-10')
    }
    function request_thumb($a, id) {
        $.ajax({
            type: 'GET',
            url: '/img/search/' + id + '?title=' + $a.attr('data-title')
        }).done(function (res) {
            console.log(res)
            $a.html(res)
            resize_detail(id)
        })
    }
    $.each($('.search_thumb'), function (_, a) {
        var id = $(a).attr('data-id')
        request_thumb($(a), id)
    })
}

