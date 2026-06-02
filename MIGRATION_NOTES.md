# Migration Notes — odoo-it-infra (14.0 → 19.0)

Repo contains one module: `it_infra`.

## Summary of changes by category

### Models

- `it_infra/models/category.py`: replaced removed `name_get(self)` with
  `_compute_display_name`. The display string is preserved byte-for-byte:
  `"%s %s" % (prefix or "", cat.name)`, where `prefix` is the recursive parent
  `display_name + " / "`. `parent_id` is only defined on the inheriting models
  (`device_category`, `supply_category`), not on this base model, so it is guarded with
  `"parent_id" in cat._fields` and intentionally left out of `@api.depends` (the
  original `name_get` likewise only touched `parent_id` on subclasses).
- `it_infra/models/software.py`: replaced removed `name_get(self)` with
  `_compute_display_name`. Both branches reproduce the exact original strings: for OS
  category `"%s %s %s" % (name, version or "", architecture or "")`, otherwise
  `"%s %s" % (name, version or "")`. `@api.depends` covers `name`, `version`,
  `architecture`, `category_id.parent_id.name`.
- `it_infra/models/server.py`: `show_passwd` raised `exceptions.except_orm(title, body)`
  — `except_orm` was removed from `odoo.exceptions` long before 14.0's API and no longer
  exists in 19.0, so it was a latent runtime error. Converted to
  `exceptions.UserError(...)`, joining the original title and body strings with a
  newline to preserve both messages.
- `_sql_constraints` in `computer.py` and `server_category.py` left as-is (still valid
  in 19.0; converting is optional/style-only).
- `equipment.py` `@api.onchange("source_doc_number")` only upper-cases the value (UI
  shaping, no raise) — left as onchange. The real validation already lives in
  `@api.constrains` (`_check_doc_number`, `_check_stock_number`), which is the correct
  autosave-safe pattern for 19.0.
- No `fields_view_get`, `@api.one/@api.multi`, `read_group`, `track_visibility`,
  `view_type`, `_translate`, `xmlid_to_res_id`, or `_cr/_uid/_context` usages found. No
  single-record `create` to convert.

### Views

- Converted all 16 `states="..."` attributes on header buttons (4 each in
  `server_views.xml`, `workstation_views.xml`, `network_device_views.xml`,
  `device_views.xml`) to `invisible="state not in [...]"` expressions, preserving exact
  state semantics (button visible only in the listed states).
- Converted all 6 `attrs="{...}"` to direct attributes (see "attrs conversions to
  review" for the compound ones).
- Converted all `<tree>`/`</tree>` to `<list>`/`</list>` (15 occurrences across
  device_category, location, software, provider, server_category, network_device_port,
  supply_category, software_category, server, workstation, network_device, device,
  supply views).
- Converted all `<field name="view_mode">tree,form</field>` to `list,form` (18
  occurrences) and the two `act_window` `view_ids` evals in `supply_views.xml`
  (`'view_mode': 'tree'` → `'list'`).
- Hidden tree columns that used `invisible="True"` on a column were changed to
  `column_invisible="True"` inside `<list>` (server/workstation/network_device `state`,
  device `device_category_id`). Form-level `invisible="True"` attributes (e.g. `server`
  `internal_location`, `supply` `is_pendrive`) were left unchanged.
- record xmlids containing `_tree` (e.g. `server_view_tree`) were NOT renamed — only the
  tag/content inside `arch` changed.
- No `t-esc`, `tree_view_ref`, `oe_chatter`, or `assets_backend` present.

### Security

- `security/ir.model.access.csv`: columns unchanged (correct for 19.0).
- `security/it_infra_groups.xml`: `res.groups` records carry
  `<field name="category_id" ref="module_category_it_infra"/>`. In 19.0 this may need
  migrating to a `privilege_id`/privilege record. Per spec this is a non-trivial change
  — LEFT AS-IS and flagged below. No `groups_id` fields exist in any data record.

### Tests

- None present.

### Manifests

- `it_infra/__manifest__.py`: `version` `14.0.1.0.0` → `19.0.1.0.0`. Added
  `"depends": ["base"]` — the module had no `depends` key but uses core models
  (`res.users`, `res.partner`) and is an application, so `base` is the real (previously
  implicit) dependency. No mail/chatter/tracking is used, so `mail` was intentionally
  NOT added. `license` already `AGPL-3`, `installable` already `True`; no dead
  `"qweb": []` key present. Data load order verified (groups → access csv → data →
  menus/views).

## 18.0 branch

- An `18.0` branch existed but was a pointer-only copy of `14.0` (empty diff); it was
  ignored per instructions. Branch `19.0` created fresh from `14.0`.

## Removed dependencies

- None removed.

## Dependencies to verify before push

- `base` — Odoo core; always present. No external/OCA dependencies.

## attrs conversions to review

Compound-domain conversions (single-tuple ones omitted):

- `server_views.xml` hosted_in_id:
  `attrs="{'invisible':[('server_type', 'not in', ['vm', 'docker'])]}"` →
  `invisible="server_type not in ['vm', 'docker']"`
- `server_views.xml` Inventory group:
  `attrs="{'invisible':[('server_type', 'not in', ['bare_metal', 'bare_metal_sa', 'hypervisor'])]}"`
  → `invisible="server_type not in ['bare_metal', 'bare_metal_sa', 'hypervisor']"`
- `server_views.xml` Hosted Servers page (compound OR):
  `attrs="{'invisible':[u'|', (u'server_type', u'=', u'bare_metal_sa'), (u'hosted_in_id', u'!=', False)]}"`
  → `invisible="server_type == 'bare_metal_sa' or hosted_in_id"`
  (`hosted_in_id != False` rendered as truthiness of the m2o).

Simple single-tuple boolean conversions (listed for completeness):

- `supply_views.xml` `attrs="{'invisible':[('is_pendrive', '=', True)]}"` →
  `invisible="is_pendrive"` (two occurrences: a group and the notebook).
- `supply_views.xml` `attrs="{'invisible':[('is_pendrive', '=', False)]}"` →
  `invisible="not is_pendrive"`.

## Autosave / onchange → constrains conversions

- None required. The only `@api.onchange` (`equipment.onchange_source_doc_number`) is
  pure UI shaping (uppercasing) with no raise. Invariants are already enforced via
  `@api.constrains`.

## Items left for human review

- `security/it_infra_groups.xml`: the two `res.groups` records set
  `<field name="category_id" ref="module_category_it_infra"/>` pointing at an
  `ir.module.category`. Odoo 19.0 reworks group categorisation toward
  `res.groups.privilege` / `privilege_id`. This was deliberately NOT changed (no
  guessing of a privilege record). Verify the correct 19.0 form before deploy.
- `server.py` `show_passwd`: `except_orm` → `UserError` collapses the former two-field
  (title/body) dialog into a single message with a newline. Confirm the UX is
  acceptable; this is the closest faithful 19.0 equivalent.
- Many models pair `_name` with `_inherit = "it_infra.<parent>"` (classic
  prototype-inheritance extension chain). This is valid and intentional, not a 19.0
  breakage — left untouched.

## Lint findings

Auto-fixers (ruff-format, prettier-xml, end-of-file/whitespace) were applied and
now pass. Remaining reporter findings (non-blocking, deliberately not chased):

- `manifest-required-author` / `missing-readme` (pylint-odoo OCA rcfile): this is
  a private module, not an OCA addon — expected, not changed.
- `prefer-env-translation` (`equipment.py`, `server.py`): 19.0 prefers
  `self.env._(...)` over the module-level `_`. Valid future cleanup; still works.
- `translation-not-lazy` (`server.py:show_passwd`): the converted `UserError`
  uses `_("...") % x`; lazy formatting is a style preference, left as-is.
- `no-raise-unlink` (`server.py:unlink`): pre-existing pattern (server unlink
  guards against deleting non-draft servers). Behavioral, not a 19.0 break —
  left untouched.
- `UP031` (% formatting) / `UP008` (`super(Server, self)`): ruff style hints in
  the two ported `_compute_display_name` methods and `unlink`. Left as-is — the
  `%` strings are reproduced verbatim from the old `name_get` to guarantee an
  identical display value.
- `unknown-option-value` warnings come from the canonical OCA `.pylintrc` listing
  message names not present in this pylint-odoo version — harmless; canonical
  file kept verbatim.

## Translations

- Translation regeneration deferred to a later stage. `i18n/es_AR.po` left as-is.
  </content> </invoke>
