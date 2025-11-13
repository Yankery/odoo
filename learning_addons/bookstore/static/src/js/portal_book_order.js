/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', function() {
    const orderBtn = document.getElementById('btn_order_book');

    if (orderBtn) {
        orderBtn.addEventListener('click', async function(e) {
            e.preventDefault();

            const bookId = this.getAttribute('data-book-id');
            const quantity = document.getElementById('book_quantity').value;
            const messageDiv = document.getElementById('order_message');

            // Disable button during request
            orderBtn.disabled = true;
            orderBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Processing...';

            try {
                const result = await jsonrpc('/my/book/order', {
                    book_id: bookId,
                    quantity: parseInt(quantity)
                });

                if (result.success) {
                    messageDiv.innerHTML = `
                        <div class="alert alert-success alert-dismissible fade show" role="alert">
                            <i class="fa fa-check-circle"></i> ${result.message}
                            <a href="/my/orders/${result.order_id}" class="alert-link">View Order</a>
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    `;

                    // Reload page after 2 seconds to update stock
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    messageDiv.innerHTML = `
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            <i class="fa fa-exclamation-triangle"></i> ${result.error}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                    `;
                    orderBtn.disabled = false;
                    orderBtn.innerHTML = '<i class="fa fa-shopping-cart"></i> Add to Order';
                }
            } catch (error) {
                messageDiv.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="fa fa-exclamation-triangle"></i> An error occurred. Please try again.
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
                orderBtn.disabled = false;
                orderBtn.innerHTML = '<i class="fa fa-shopping-cart"></i> Add to Order';
                console.error('Order error:', error);
            }
        });
    }
});