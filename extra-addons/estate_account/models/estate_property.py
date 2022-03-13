from odoo import fields, models, api, _, exceptions


class Property(models.Model):
    _inherit = "estate.property"

    # override sold action
    def sold_property(self):
        print("WOW IT WORK")
        #sudo bypass right and rules
        journal = self.env['account.move'].with_context(default_move_type='out_invoice').sudo()._get_default_journal()

        # create invoice line
        invoice_lines = [
            {
                "name": self.name,
                "quantity": 1,
                "price_unit": (self.selling_price * 6) / 100
             },
            {
                "name": "Administrative fees",
                "quantity": 1,
                "price_unit": 100
            }
        ]

        account_move = self.env['account.move'].sudo().create({
            'partner_id': self.buyer_id.id,
            'move_type': "out_invoice",
            'journal_id': journal.id,
            'invoice_line_ids': invoice_lines
        })

        return super().sold_property()
