from odoo import fields, models, api


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = 'sequence, name'

    name = fields.Char(string="Type", required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string="Properties")
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer("Offer", compute='_compute_offer_count')


    _sql_constraints = [
        ('check_name', 'UNIQUE(name)', 'The type name must be unique'),
    ]

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            count = 0
            for item in record.offer_ids:
                count += 1
            record.offer_count = count


