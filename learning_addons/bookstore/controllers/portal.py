# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class BookstorePortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """Add book orders count to portal home"""
        values = super()._prepare_home_portal_values(counters)
        if "book_order_count" in counters:
            book_order_count = (
                request.env["bookstore.order"].search_count(
                    [("partner_id", "=", request.env.user.partner_id.id)]
                )
                if request.env.user.partner_id
                else 0
            )
            values["book_order_count"] = book_order_count
        return values

    @http.route(
        ["/my/books", "/my/books/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_books(
        self, page=1, sort_by=None, filter_by=None, search=None, search_in="name", **kw
    ):
        """Display available books for ordering"""
        values = self._prepare_portal_layout_values()
        book = request.env["bookstore.book"]

        searchbar_sorting = {
            "name": {"label": "Name", "order": "name"},
            "date": {"label": "Published Date", "order": "published_date desc"},
            "price": {"label": "Price", "order": "list_price"},
        }

        searchbar_filters = {
            "all": {"label": "All", "domain": [("quantity", ">", 0)]},
            "available": {"label": "In Stock", "domain": [("quantity", ">", 10)]},
        }

        searchbar_inputs = {
            "name": {"input": "name", "label": "Search in Name"},
            "author": {"input": "author", "label": "Search in Author"},
        }

        # Default sort and filter
        if not sort_by:
            sort_by = "name"
        order = searchbar_sorting[sort_by]["order"]

        if not filter_by:
            filter_by = "all"
        domain = searchbar_filters[filter_by]["domain"]

        # Search
        if search and search_in:
            search_domain = []
            if search_in == "name":
                search_domain = [("name", "ilike", search)]
            elif search_in == "author":
                search_domain = [("author_ids.name", "ilike", search)]
            domain += search_domain

        # Count books
        book_count = book.search_count(domain)
        print("Book count:", book_count)

        # Pager
        pager = portal_pager(
            url="/my/books",
            url_args={
                "sort_by": sort_by,
                "filter_by": filter_by,
                "search_in": search_in,
                "search": search,
            },
            total=book_count,
            page=page,
            step=12,
        )

        # Get books
        books = book.search(domain, order=order, limit=12, offset=pager["offset"])

        values.update(
            {
                "books": books,
                "page_name": "book_catalog",
                "pager": pager,
                "default_url": "/my/books",
                "searchbar_sorting": searchbar_sorting,
                "searchbar_filters": searchbar_filters,
                "searchbar_inputs": searchbar_inputs,
                "sort_by": sort_by,
                "filter_by": filter_by,
                "search_in": search_in,
                "search": search,
            }
        )

        return request.render("bookstore.portal_my_books", values)

    @http.route(["/my/books/<int:book_id>"], type="http", auth="user", website=True)
    def portal_book_detail(self, book_id, **kw):
        """Display book details"""
        try:
            book = request.env["bookstore.book"].browse(book_id)
            if not book.exists() or book.quantity <= 0:
                return request.redirect("/my/books")
        except (AccessError, MissingError):
            return request.redirect("/my/books")

        values = {
            "book": book,
            "page_name": "book_detail",
        }

        return request.render("bookstore.portal_book_detail", values)

    @http.route(["/my/book/order"], type="json", auth="user", methods=["POST"])
    def create_book_order(self, book_id, quantity=1, **kw):
        """Create a book order via AJAX"""
        try:
            book = request.env["bookstore.book"].browse(int(book_id))
            if not book.exists():
                return {"error": "Book not found"}

            if book.quantity < int(quantity):
                return {"error": f"Only {book.quantity} books available in stock"}

            # Create order
            order = (
                request.env["bookstore.order"]
                .sudo()
                .create(
                    {
                        "partner_id": request.env.user.partner_id.id,
                        "book_id": book.id,
                        "quantity": int(quantity),
                        "unit_price": book.list_price,
                        "total_price": book.list_price * int(quantity),
                        "state": "draft",
                    }
                )
            )

            # Update book quantity
            book.sudo().write({"quantity": book.quantity - int(quantity)})

            return {
                "success": True,
                "order_id": order.id,
                "message": "Order created successfully!",
            }
        except Exception as e:
            return {"error": str(e)}

    @http.route(
        ["/my/orders", "/my/orders/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_orders(self, page=1, sort_by=None, **kw):
        """Display user's book orders"""
        values = self._prepare_portal_layout_values()
        Order = request.env["bookstore.order"]

        searchbar_sorting = {
            "date": {"label": "Order Date", "order": "create_date desc"},
            "name": {"label": "Book Name", "order": "book_id"},
            "state": {"label": "Status", "order": "state"},
        }

        if not sort_by:
            sort_by = "date"
        order = searchbar_sorting[sort_by]["order"]

        domain = [("partner_id", "=", request.env.user.partner_id.id)]

        # Count orders
        order_count = Order.search_count(domain)

        # Pager
        pager = portal_pager(
            url="/my/orders",
            url_args={"sort_by": sort_by},
            total=order_count,
            page=page,
            step=10,
        )

        # Get orders
        orders = Order.search(domain, order=order, limit=10, offset=pager["offset"])

        values.update(
            {
                "orders": orders,
                "page_name": "my_orders",
                "pager": pager,
                "default_url": "/my/orders",
                "searchbar_sorting": searchbar_sorting,
                "sort_by": sort_by,
            }
        )

        return request.render("bookstore.portal_my_orders", values)

    @http.route(["/my/orders/<int:order_id>"], type="http", auth="user", website=True)
    def portal_order_detail(self, order_id, **kw):
        """Display order details"""
        try:
            order = request.env["bookstore.order"].browse(order_id)
            if (
                not order.exists()
                or order.partner_id.id != request.env.user.partner_id.id
            ):
                return request.redirect("/my/orders")
        except (AccessError, MissingError):
            return request.redirect("/my/orders")

        values = {
            "order": order,
            "page_name": "order_detail",
        }

        return request.render("bookstore.portal_order_detail", values)
