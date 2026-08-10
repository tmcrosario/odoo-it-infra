from odoo import _, exceptions, fields, models


class Server(models.Model):
    _name = "it_infra.server"
    _description = "Server"
    _inherit = "it_infra.computer"

    _server_type_ = [
        ("bare_metal", "Bare Metal"),
        ("bare_metal_sa", "Bare Metal (Standalone)"),
        ("cloud", "Cloud"),
        ("hypervisor", "Hypervisor"),
        ("vm", "Virtual Machine"),
        ("docker", "Docker Stack"),
    ]

    open_ports = fields.Char(groups="it_infra.group_manager")

    server_type = fields.Selection(selection=_server_type_)

    category_ids = fields.Many2many(
        comodel_name="it_infra.server_category",
        relation="server_category_rel",
        string="Categories",
    )

    location_id = fields.Many2one(comodel_name="it_infra.location", required=True)

    internal_location = fields.Boolean(related="location_id.internal")

    webadmin = fields.Char(string="Web Admin", groups="it_infra.group_manager")

    hosted_in_id = fields.Many2one(comodel_name="it_infra.server")

    hosted_server_ids = fields.One2many(
        comodel_name="it_infra.server",
        inverse_name="hosted_in_id",
        readonly=True,
    )

    def unlink(self):
        # Validate every record before deleting any; returning inside the
        # loop used to delete the rest without checking their state
        for server in self:
            if server.state != "draft":
                raise exceptions.UserError(
                    _("You cannot delete a server which is not in draft state.")
                )
        return super().unlink()
