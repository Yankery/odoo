# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ModelName(models.Model):
    _name = "bookstore.author"
    _description = "Author of Books"
    _order = "name asc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True)
    avatar = fields.Binary(string="Avatar")
    biography = fields.Text(string="Biography")
    date_of_birth = fields.Date(string="Date of Birth")
    book_ids = fields.Many2many(
        "bookstore.book",
        relation="bookstore_author_book_rel",
        column1="author_id",
        column2="book_id",
        string="Books",
    )
    unique_title_count = fields.Integer(
        string="Number of Unique Titles",
        compute="_compute_unique_title_count",
        store=True,
    )

    _sql_constraints = []

    @api.depends("book_ids")
    def _compute_unique_title_count(self):
        for author in self:
            author.unique_title_count = len(author.book_ids)
