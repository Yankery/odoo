# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Book(models.Model):
    _name = "bookstore.book"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _inherits = {"product.template": "product_tmpl_id"}
    _description = "Books in the Bookstore"
    _order = "name asc"

    product_tmpl_id = fields.Many2one(
        "product.template",
        "Product Template",
        required=True,
        ondelete="cascade",
        auto_join=True,
    )

    published_date = fields.Date(string="Published Date")
    pages = fields.Integer(string="Number of Pages", default=0)
    cover = fields.Binary(string="Book Cover")
    language = fields.Char(string="Language")
    rental_price = fields.Float(string="Rental Price")
    quantity = fields.Integer(string="Quantity in Stock", default=0)

    author_ids = fields.Many2many(
        "bookstore.author",
        relation="bookstore_author_book_rel",
        column1="book_id",
        column2="author_id",
        string="Authors",
    )
    is_published = fields.Boolean(
        string="Published in Portal",
        default=False,
        help="If checked, this book will be visible in the customer portal",
        tracking=True,
    )

    _sql_constraints = []

    _barcode_scanned_field = "barcode"

    def action_publish(self):
        """Publish book to portal"""
        for book in self:
            vals = {"is_published": True}
            if hasattr(book, "website_published"):
                vals["website_published"] = True
            if hasattr(book, "sale_ok"):
                vals["sale_ok"] = True
            book.write(vals)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Published!",
                "message": f"{len(self)} book(s) published successfully.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_unpublish(self):
        """Unpublish book from portal"""
        for book in self:
            vals = {"is_published": False}
            if hasattr(book, "website_published"):
                vals["website_published"] = False
            book.write(vals)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Unpublished!",
                "message": f"{len(self)} book(s) unpublished.",
                "type": "warning",
                "sticky": False,
            },
        }

    @api.constrains("list_price", "rental_price")
    def _check_prices(self):
        for book in self:
            if book.list_price < 0:
                raise ValidationError("Sale price cannot be negative.")
            if book.rental_price < 0:
                raise ValidationError("Rental price cannot be negative.")
            if book.list_price < book.rental_price:
                raise ValidationError("Sale price must be ≥ Rental price.")

    @api.constrains("barcode")
    def _check_isbn_unique(self):
        for book in self:
            if book.barcode:
                duplicate = self.env["bookstore.book"].search(
                    [("barcode", "=", book.barcode), ("id", "!=", book.id)], limit=1
                )
                if duplicate:
                    raise ValidationError(
                        f"The ISBN '{book.barcode}' is already used by another book."
                    )

    @api.onchange("list_price")
    def _onchange_list_price(self):
        if self.list_price < 0:
            self.list_price = 0.0
        self.rental_price = self.list_price * 0.1
        self.standard_price = self.list_price / 2

    @api.onchange("standard_price")
    def _onchange_standard_price(self):
        if self.standard_price < 0:
            self.standard_price = 0.0
        self.list_price = self.standard_price * 2
        self.rental_price = self.standard_price * 0.1

    @api.onchange("rental_price")
    def _onchange_rental_price(self):
        if self.rental_price < 0:
            self.rental_price = 0.0
        self.list_price = self.rental_price * 10
        self.standard_price = self.rental_price * 5
