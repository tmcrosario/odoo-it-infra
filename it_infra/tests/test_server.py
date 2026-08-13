from odoo.exceptions import UserError
from odoo.tests import common


class TestServer(common.TransactionCase):
    def setUp(self):
        super().setUp()
        category = self.env["it_infra.software_category"].create({"name": "OS"})
        self.software = self.env["it_infra.software"].create(
            {"name": "Linux", "category_id": category.id}
        )
        self.location = self.env["it_infra.location"].create({"name": "DC"})

    def _server(self, name):
        return self.env["it_infra.server"].create(
            {
                "name": name,
                "username": "admin",
                "os_id": self.software.id,
                "location_id": self.location.id,
            }
        )

    def test_unlink_guards_every_record(self):
        # A non-draft server anywhere in the set must block the whole delete;
        # returning inside the loop used to delete the rest unchecked
        draft = self._server("srv-draft")
        active = self._server("srv-active")
        active.action_active()

        with self.assertRaises(UserError):
            (draft + active).unlink()

        self.assertTrue(draft.exists())
        self.assertTrue(active.exists())

    def test_unlink_draft_succeeds(self):
        draft = self._server("srv-only-draft")
        draft.unlink()
        self.assertFalse(draft.exists())
