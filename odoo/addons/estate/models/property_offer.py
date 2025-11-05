from datetime import timedelta
from odoo import models, fields, api
from odoo.addons.estate.consts import (
    PROPERTY_OFFER_STATUS_CHOICES,
    PropertyOfferStatus,
    EstateState,
)
from odoo.exceptions import UserError


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc"

    price = fields.Float(string="Offer Price")
    status = fields.Selection(PROPERTY_OFFER_STATUS_CHOICES)
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )
    property_id = fields.Many2one("estate.property", string="Properties", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)

    SQL_CONSTRAINTS = [
        ("price_positive", "CHECK(price >= 0)", "The offer price must be positive."),
    ]

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for record in self:
            create_date = (
                record.create_date.date() if record.create_date else fields.Date.today()
            )
            record.date_deadline = create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            create_date = (
                record.create_date.date() if record.create_date else fields.Date.today()
            )
            if record.date_deadline:
                record.validity = (record.date_deadline - create_date).days
            else:
                record.validity = 0

    def action_accept(self):
        for record in self:
            if record.property_id.state == EstateState.SOLD:
                raise UserError("The property is already sold.")
            record.status = PropertyOfferStatus.ACCEPTED
            record.property_id.state = EstateState.SOLD
            # Refuse other offers for the same property
            other_offers = self.search(
                [
                    ("property_id", "=", record.property_id.id),
                    ("id", "!=", record.id),
                    (
                        "status",
                        "not in",
                        [PropertyOfferStatus.REFUSED],
                    ),
                ]
            )
            other_offers.write({"status": PropertyOfferStatus.REFUSED})

    def action_refuse(self):
        for record in self:
            if record.status == PropertyOfferStatus.REFUSED:
                raise UserError("This offer has already been refused.")
            record.status = PropertyOfferStatus.REFUSED
