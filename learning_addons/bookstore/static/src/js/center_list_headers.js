odoo.define('bookstore.center_list_headers', function (require) {
    'use strict';

    const ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        _renderView: function () {
            const self = this;
            return this._super.apply(this, arguments).then(() => {
                // Target only bookstore.book or all if preferred
                const $table = self.$el.find('.o_list_table');
                if ($table.length) {
                    $table.find('th').css({
                        'text-align': 'center',
                        'justify-content': 'center'
                    }).removeAttr('style'); // Remove inline styles first
                    $table.find('th').css('text-align', 'center');
                }
            });
        },

        // Re-apply on column sort, resize, etc.
        _onSortColumn: function () {
            this._super.apply(this, arguments);
            this._centerHeaders();
        },

        _centerHeaders: function () {
            this.$el.find('.o_list_table th').css('text-align', 'center');
        }
    });

    // Re-apply after any update
    const { onRendered } = ListRenderer.prototype;
    ListRenderer.prototype.onRendered = function () {
        onRendered.apply(this, arguments);
        this._centerHeaders();
    };
});