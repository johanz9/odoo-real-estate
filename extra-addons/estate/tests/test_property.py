from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError
from odoo.tests import tagged

# The CI will run these tests after all the modules are installed,
# not right after installing the one defining it.
@tagged('post_install', '-at_install')
class TestPropertyOffer(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPropertyOffer, cls).setUpClass()
        type = cls.env.ref('estate.demo_land')

        cls.property01 = cls.env['estate.property'].create({
            'name': 'Test House',
            'state': 'Sold',
            'postcode': 4000,
            'expected_price': 4000,
            'living_area': 10,
            'facades': 4,
            'garage': False,
            'garden': True,
            'garden_area': 10,
            'property_type_id': type.id
        })
        cls.property02 = cls.env['estate.property'].create({
            'name': 'Test House',
            'state': 'New',
            'postcode': 4000,
            'expected_price': 4000,
            'living_area': 10,
            'facades': 4,
            'garage': False,
            'garden': True,
            'garden_area': 10,
            'property_type_id': type.id
        })

    def test_state(self):
        property = self.property01
        self.assertEqual(property["state"], 'Sold')

    def test_add_offer_to_property_sold(self):
        property = self.property01
        partner = self.env.ref('base.res_partner_12')

        with self.assertRaises(UserError), self.cr.savepoint():
            self.offer = self.env['estate.property.offer'].create({
                'price': 20000,
                'partner_id': partner.id,
                'property_id': property.id,
            })

    def test_property_offer_recevied_state(self):
        property = self.property02
        partner = self.env.ref('base.res_partner_12')
        self.offer = self.env['estate.property.offer'].create({
            'price': 20000,
            'partner_id': partner.id,
            'property_id': property.id,
        })
        self.assertEqual(property["state"], 'Offer Received')




