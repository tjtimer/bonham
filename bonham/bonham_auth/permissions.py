__all__ = ['is_superuser_or_owner', 'is_admin_or_owner', 'is_editor']

async def is_superuser_or_owner(account, obj):
    return account['is_superuser'] or account['id'] is obj['owner']


async def is_admin_or_owner(connection, account, obj):
    if not account['is_superuser'] or account['id'] is obj['owner']:
        where = f"account_id={account['id']} AND table='{obj['table']}' AND " \
                f"object_id={obj['id']}"
        is_admin_stmt = f"SELECT id FROM {obj['table']}_admin WHERE {where}"
        is_admin = await connection.fetchval(is_admin_stmt)
        if not is_admin:
            return False
    return True


async def is_editor(connection, account, obj):
    if not await is_admin_or_owner(connection, account, obj):
        where = f"account_id={account['id']} AND table='{obj['table']}' AND object_id={obj['id']}"
        is_editor_stmt = f"SELECT id FROM {obj['table']}_editor WHERE {where}"
        is_editor = await connection.fetchval(is_editor_stmt)
        print(f"is_editor\nis_editor: {is_editor}")
        if not is_editor:
            return False
    return True
