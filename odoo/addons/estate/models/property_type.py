from odoo import models, fields


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _order = "name asc"

    name = fields.Char(string="Name", required=True)
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )
    sequence = fields.Integer(string="Sequence", default=1)

    SQL_CONSTRAINTS = [
        ("name_unique", "UNIQUE(name)", "The type name must be unique."),
    ]
