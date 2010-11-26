
$(function() {
    var inline = $('.dynamic-inline .table');
    inline.sortable({handle: '.ordering', axis: 'y', opacity: '.7'});
    inline.disableSelection();
    inline.find('.ordering').css({cursor: 'move'});
    inline.closest('form').submit(function() {
        $('.dynamic-form:not(.predelete)', inline).each(function(i) {
            $('._order > input', this).val(i);
        });
    });
});
