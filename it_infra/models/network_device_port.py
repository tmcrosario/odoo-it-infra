from odoo import fields, models


class NetworkDevicePort(models.Model):
    _name = "it_infra.network_device_port"
    _description = "Network Device Port"

    _cable_colors_ = [
        ("blue", "Blue"),
        ("yellow", "Yellow"),
        ("white", "White"),
        ("gray", "Gray"),
        ("black", "Black"),
    ]

    name = fields.Char()

    mac_address = fields.Char()

    ip_address = fields.Char()

    netmask = fields.Char(default="/24")

    state = fields.Boolean(string="Active")

    vlan = fields.Char()

    inter_vlan_routing = fields.Char()

    # A port records whatever is plugged into it, of any equipment type
    connected_to = fields.Reference(
        selection=[
            ("it_infra.computer", "Computer"),
            ("it_infra.workstation", "Workstation"),
            ("it_infra.server", "Server"),
            ("it_infra.device", "Device"),
            ("it_infra.network_device", "Network Device"),
        ],
    )

    cable_color = fields.Selection(selection=_cable_colors_)

    network_device_id = fields.Many2one(comodel_name="it_infra.network_device")
