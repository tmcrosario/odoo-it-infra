from odoo import fields, models


class ServerCategory(models.Model):
    _name = "it_infra.server_category"
    _description = "Server Category"

    name = fields.Char(required=True)

    server_ids = fields.Many2many(
        comodel_name="it_infra.server",
        relation="server_category_rel",
        column1="it_infra_server_category_id",
        column2="it_infra_server_id",
        string="Servers",
    )

    parent_id = fields.Many2one(
        comodel_name="it_infra.server_category", string="Parent"
    )

    child_ids = fields.One2many(
        comodel_name="it_infra.server_category",
        inverse_name="parent_id",
        string="Childs",
    )

    _name_uniq = models.Constraint("unique(name)", "Server tags must be unique!")
