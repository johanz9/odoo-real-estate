from odoo import fields, models, api, _, exceptions
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import datetime

from odoo.tools import float_compare, float_is_zero

SELECTION = [
    ('North', 'North'),
    ('South', 'South'),
    ('East', 'East'),
    ('West', 'West'),
]


def add_months(months=1):
    date_after_month = datetime.datetime.today() + relativedelta(months)
    return date_after_month.strftime('%Y-%m-%d')


def parse_datetime(date_to_convert):
    pattern = "%Y-%m-%d"
    return datetime.datetime.strptime(date_to_convert, pattern)


class Property(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = 'id desc'

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string="Postcode", required=True)
    date_availability = fields.Date(string="Available From",
                                    required=True,
                                    default=add_months(3),
                                    # default=lambda self: fields.Datetime.now()),
                                    copy=False)
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", required=True, default=2)
    living_area = fields.Integer(string="Living Area (sqm)", required=True)
    facades = fields.Integer(string="Facades", required=True)
    garage = fields.Boolean(string="Garage", required=False)
    garden = fields.Boolean(string="Garden", required=False)
    garden_area = fields.Integer(string="Garden Area (sqm)", required=False)
    garden_orientation = fields.Selection(string='Garden Orientation', selection=SELECTION, help="Help example")

    active = fields.Boolean(string='Active', default=True, invisible=True)
    state = fields.Selection([
        ('New', 'New'),
        ('Offer Received', 'Offer Received'),
        ('Offer Accepted', 'Offer Accepted'),
        ('Sold', 'Sold'),
        ('Canceled', 'Canceled')], 'Status', default='New',
        store=True)

    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer', ondelete="set null", copy=False)
    salesman_id = fields.Many2one('res.users', string='Salesman', index=True,
                                  default=lambda self: self.env.uid)
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Integer(string="Total Area", compute="_compute_total")
    best_price = fields.Float(string="Best Price", compute="_get_best_price")
    color = fields.Integer(string="Index Color", default=0)

    company_id = fields.Many2one('res.company', string='Company', index=True,
                                  default=lambda self: self.env.company.id)

    _sql_constraints = [
        ('check_living_area', 'CHECK(living_area >= 1)', 'The number of living area can\'t be zero or less.'),
        ('check_expected_price', 'CHECK(expected_price >= 0)', 'The expected price must be strictly positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be strictly positive'),
    ]


    # for computed field
    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _get_best_price(self):
        for record in self:
            max_value = 0
            found = False
            for item in record.offer_ids:
                if item.price >= max_value:
                    max_value = item.price
                if item.status == "Accepted":
                    found = True
            if not found:
                record.selling_price = 0
                record.buyer_id = False

            record.best_price = max_value

    # this event trigger when garden is changed
    @api.onchange("garden")
    def _onchange_partner_id(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "North"
        else:
            self.garden_area = 0
            self.garden_orientation = ""
            # return {'warning': {
            #     'title': _("Warning"), # title can be anything
            #     'message': ('Garden unsetted')}}

    def cancel_property(self):
        for record in self:
            if record.state == "Sold":
                raise exceptions.UserError('Sold properties cannot be Cancelled.')
            record.state = "Canceled"
        return True

    def sold_property(self):
        for record in self:
            if record.state == "Canceled":
                raise exceptions.UserError('Canceled properties cannot be sold.')
            record.state = "Sold"
        return True

    @api.constrains('selling_price')
    def _check_expected_selling_price(self):
        for record in self:
            if record.selling_price != 0:
                # check if selling_price is a zero
                if not float_is_zero(record.selling_price, precision_rounding=3):
                    # check if the selling price is lower of expected_price
                    if float_compare(record.selling_price, record.expected_price, precision_digits=3) < 0:
                        percentage = (record.selling_price / record.expected_price) * 100
                        if percentage < 90:
                            raise ValidationError("The selling price cannot be lower than 90% of the expected price.")

    # override unlink def
    def unlink(self):
        for record in self:
            if record.state not in ['New', 'Canceled']:
                raise exceptions.UserError('Only a new or canceled property can be deleted')
        return super(Property, self).unlink()


class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _order = 'name asc'

    name = fields.Char(string="Type", required=True)
    color = fields.Integer(string="Color", default="1")

    _sql_constraints = [
        ('check_name', 'UNIQUE(name)', 'The tag name must be unique'),
    ]


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = 'price desc'

    price = fields.Float(string="Price")
    status = fields.Selection([
        ('Accepted', 'Accepted'),
        ('Refused', 'Refused')], copy=False)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True, ondelete="cascade")
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_deadline", inverse="_inverse_deadline")
    property_type_id = fields.Many2one(related="property_id.property_type_id")

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The offer price must be strictly positive'),
    ]

    @api.depends("validity", "create_date")
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + datetime.timedelta(days=record.validity)
            else:
                record.date_deadline = datetime.date.today() + datetime.timedelta(days=record.validity)

    def _inverse_deadline(self):
        for record in self:
            if record.create_date and record.create_date != record.date_deadline:
                d1 = datetime.datetime.strptime(str(record.date_deadline), "%Y-%m-%d")
                d2 = datetime.datetime.strptime(str(record.create_date), "%Y-%m-%d %H:%M:%S.%f")
                days_from_date = (d1 - d2)
                record.validity = days_from_date.days

    def accept_offer(self):
        for record in self:
            record.status = "Accepted"
            # if selling price is greater than 0, it means that another offer was accepted
            if record.property_id.selling_price > 0:
                raise exceptions.UserError('Another offer was accepted')

            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = "Offer Accepted"

        return True

    def refuse_offer(self):
        for record in self:
            if record.status == "Accepted":
                record.property_id.selling_price = 0
                record.property_id.buyer_id = False
                record.property_id.state = "Offer Received"
            record.status = "Refused"

        return True

    @api.model
    def create(self, vals):
        property = self.env['estate.property'].browse(vals['property_id'])
        if property.state == "Sold":
            raise exceptions.UserError('Cannot add offer to sold property')

        property.state = "Offer Received"
        self.property_id = property
        return super().create(vals)
