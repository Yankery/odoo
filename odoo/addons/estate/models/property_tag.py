from odoo import models, fields


class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"
    _order = "name asc"

    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string="Color Index")

    SQL_CONSTRAINTS = [
        ("name_unique", "UNIQUE(name)", "The tag name must be unique."),
    ]
