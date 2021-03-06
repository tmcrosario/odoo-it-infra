from odoo import models, fields


class Workstation(models.Model):

    _name = 'it_infra.workstation'
    _inherit = 'it_infra.computer'

    product_key = fields.Char(size=29, tracking=True)

    office_suite_id = fields.Many2one(comodel_name='it_infra.software',
                                      string='Office Suite',
                                      domain=[('category_id.parent_id',
                                               'ilike', 'Office Suite')],
                                      tracking=True)

    workstation_maintenance_ids = fields.One2many(
        comodel_name='it_infra.workstation_maintenance',
        inverse_name='workstation_id')
