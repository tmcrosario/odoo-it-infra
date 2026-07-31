import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, exceptions, fields, models


class Equipment(models.Model):
    _name = "it_infra.equipment"
    _description = "Equipment"
    _order = "purchase_date desc"

    _states_ = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("stored", "Stored"),
        ("decommissioned", "Decommissioned"),
    ]

    @api.constrains("stock_number")
    def _check_stock_number(self):
        for rec in self:
            if rec.stock_number and len(rec.stock_number) != 4:
                raise exceptions.ValidationError(
                    _("Stock number must be 4 characters.")
                )

    __check_doc_number_re = re.compile(r"([0-9]{3}\-[A-Za-z]{3}\-[0-9]{4})$")

    @api.onchange("source_doc_number")
    def onchange_source_doc_number(self):
        if self.source_doc_number:
            if self.__check_doc_number_re.match(self.source_doc_number):
                self.source_doc_number = self.source_doc_number.upper()

    @api.constrains("source_doc_number")
    def _check_doc_number(self):
        for rec in self:
            if not rec.source_doc_number:
                continue
            if not self.__check_doc_number_re.match(rec.source_doc_number):
                raise exceptions.ValidationError(_("Invalid document format"))
            tmp = rec.source_doc_number.split("-")[2]
            input_date = datetime.strptime(tmp, "%Y")
            year_limit = datetime.today() - relativedelta(years=20)
            if input_date < year_limit or input_date > datetime.today():
                raise exceptions.ValidationError(_("Invalid document year."))

    def action_draft(self):
        self.state = "draft"

    def action_active(self):
        self.state = "active"

    def action_stored(self):
        self.state = "stored"

    def action_decommissioned(self):
        self.state = "decommissioned"

    name = fields.Char(required=True)

    description = fields.Text()

    stock_number = fields.Char(help="Format: XXXX (For example: 1234)")

    hostname = fields.Char()

    ip_address = fields.Char()

    netmask = fields.Char(default="/24")

    source_doc_number = fields.Char(
        string="Source Document",
        help="Format: XXX-AAA-YYYY (For example: 123-ABC-2014)",
    )

    purchase_date = fields.Date()

    office = fields.Char()

    warranty = fields.Integer(string="Warranty (months)", default=12)

    state = fields.Selection(selection=_states_, default="draft")
