from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many("estate.property", "salesman_id", string="Properties")
    #karma = fields.Integer(string='Karma', default=0)
