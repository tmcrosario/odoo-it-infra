from odoo import api, fields, models


class Category(models.Model):

    _name = "it_infra.category"
    _description = "Category"

    name = fields.Char(required=True)

    @api.depends("name")
    def _compute_display_name(self):
        # NOTE: ``parent_id`` is defined on the inheriting models
        # (device_category, supply_category), not on this base model, so it is
        # intentionally not part of @api.depends here.
        for cat in self:
            prefix = None
            if "parent_id" in cat._fields and cat.parent_id:
                prefix = cat.parent_id.display_name + " / "
            cat.display_name = "%s %s" % (prefix or "", cat.name)
