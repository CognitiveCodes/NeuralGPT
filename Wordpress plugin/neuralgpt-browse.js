jQuery(document).ready(function($) {
    $('#neuralgpt-browse-form').on('submit', function(e) {
        e.preventDefault();
        var searchQuery = $('#neuralgpt-browse-search').val();
        $.ajax({
            url: '/wp-json/neuralgpt-browse/v1/search',
            type: 'POST',
            data: {
                'search_query': searchQuery
            },
            success: function(response) {
                $('#neuralgpt-browse-results').empty();
                $.each(response, function(index, value) {
                    var listItem = $('<li>');
                    var link = $('<a>').attr('href', value.link).text(value.title);
                    var excerpt = $('<p>').text(value.excerpt);
                    listItem.append(link).append(excerpt);
                    $('#neuralgpt-browse-results').append(listItem);
                });
            }
        });
    });
});