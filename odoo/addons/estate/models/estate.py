from datetime import date, timedelta

from odoo import models, fields, api
from odoo.addons.estate.consts import (
    GARDEN_ORIENTATION_CHOICES,
    ESTATE_STATE_CHOICES,
    EstateState,
    GardenOrientation,
)
from odoo.exceptions import UserError


class EstateModel(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    name = fields.Char(string="Property Name", required=True)
    description = fields.Text(string="Description")
    price = fields.Float(string="Price", required=True)
    available = fields.Boolean(string="Available", default=True)
    date_available = fields.Date(
        string="Date Available",
        default=date.today() + timedelta(days=90),
        copy=False,
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    bathrooms = fields.Integer(string="Bathrooms", default=1)
    living_area = fields.Integer(string="Living Area (sqm)", default=0)
    garden = fields.Boolean(string="Garden", default=False)
    garage = fields.Boolean(string="Garage", default=False)
    garden_area = fields.Integer(string="Garden Area (sqm)", default=0)
    garden_orientation = fields.Selection(
        GARDEN_ORIENTATION_CHOICES, string="Garden Orientation"
    )
    total_area = fields.Integer(
        string="Total Area (sqm)", compute="_compute_total_area"
    )
    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        ESTATE_STATE_CHOICES, string="State", default=EstateState.NEW, required=True
    )
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    best_price = fields.Float(string="Best Offer Price", compute="_compute_best_price")
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")

    _sql_constraints = [
        ("price_positive", "CHECK(price >= 0)", "The price must be positive."),
        (
            "best_price_positive",
            "CHECK(best_price >= 0)",
            "The best price must be positive.",
        ),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        for record in self:
            if not record.garden:
                record.garden_area = 0
                record.garden_orientation = False
            else:
                record.garden_area = 10
                record.garden_orientation = GardenOrientation.NORTH

    @api.constrains("name")
    def _limit_name(self):
        for record in self:
            if len(record.name) < 5:
                raise UserError("The property name must be at least 5 characters long.")
            if len(record.name) > 50:
                raise UserError("The property name must not exceed 50 characters.")

    # Action methods

    def action_sold(self):
        for record in self:
            if record.state == EstateState.CANCELED:
                raise UserError("Cancelled properties cannot be sold.")
            record.state = EstateState.SOLD

    def action_cancel(self):
        for record in self:
            if record.state == EstateState.SOLD:
                raise UserError("Sold properties cannot be cancelled.")
            record.state = EstateState.CANCELED
