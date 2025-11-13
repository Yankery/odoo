# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class BookstoreOrder(models.Model):
    _name = "bookstore.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Book Order"
    _order = "create_date desc"

    name = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True
    )
    book_id = fields.Many2one(
        "bookstore.book", string="Book", required=True, tracking=True
    )
    quantity = fields.Integer(
        string="Quantity", default=1, required=True, tracking=True
    )
    unit_price = fields.Float(string="Unit Price", required=True, tracking=True)
    total_price = fields.Float(
        string="Total Price", compute="_compute_total_price", store=True, tracking=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("processing", "Processing"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    order_date = fields.Datetime(
        string="Order Date", default=fields.Datetime.now, tracking=True
    )
    notes = fields.Text(string="Notes")

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("bookstore.order") or "New"
            )
        return super(BookstoreOrder, self).create(vals)

    @api.depends("quantity", "unit_price")
    def _compute_total_price(self):
        for order in self:
            order.total_price = order.quantity * order.unit_price

    @api.constrains("quantity")
    def _check_quantity(self):
        for order in self:
            if order.quantity <= 0:
                raise ValidationError("Quantity must be greater than zero.")

    def action_confirm(self):
        """Confirm the order"""
        for order in self:
            if order.state == "draft":
                order.state = "confirmed"

    def action_process(self):
        """Mark order as processing"""
        for order in self:
            if order.state == "confirmed":
                order.state = "processing"

    def action_deliver(self):
        """Mark order as delivered"""
        for order in self:
            if order.state == "processing":
                order.state = "delivered"

    def action_cancel(self):
        """Cancel the order and restore book quantity"""
        for order in self:
            if order.state in ["draft", "confirmed"]:
                # Restore book quantity
                order.book_id.sudo().write(
                    {"quantity": order.book_id.quantity + order.quantity}
                )
                order.state = "cancelled"
