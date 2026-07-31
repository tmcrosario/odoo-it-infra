def migrate(cr, version):
    # connected_to moved from Many2one (integer FK) to Reference (varchar);
    # drop the stale integer column so the ORM recreates it with the new type
    cr.execute(
        "ALTER TABLE it_infra_network_device_port "
        "DROP COLUMN IF EXISTS connected_to"
    )
