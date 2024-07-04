function get_extra_products(group_id) {
    (function($){
        var extraProductsSelect = $('#id_card_code-0-extra_products_from');
        var card_id = window.location.pathname.split('/')[4];
        if (card_id === 'add') {
            card_id = '0';
        }
        console.log(card_id)
        if (group_id) {
            //console.log(group_id)
            $.ajax({
                url: '/services/admin/filtered-products/' + group_id + '/' + card_id + '/',
                success: function(data) {
                    console.log(data)
                    extraProductsSelect.empty();
                    $.each(data, function(index, product) {
                        extraProductsSelect.append($('<option>', {
                            value: product.id,
                            text: product.title
                        }));
                    });
                },
                error: function(xhr, status, error) {
                    console.error('Error:', status, error);
                }
            });
        } else {
            extraProductsSelect.empty();
        }
    })(django.jQuery);
};