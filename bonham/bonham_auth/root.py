"""
Bonham Auth
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 0.0.1dev
Auth flow:
    - user creates account / signs in with email and password  # TODO: or
    oAuth(2)
    - user gets mail with link containing the activation key
    - user clicks link in mail
    - account gets activated and user gets logged in
    - login:
        -> create refresh token and save to db (used to create new access token)
        -> set cookie with refresh token
                used on page request and if access token has expired
        -> create access token (used for API requests; don't save anywhere)
        -> add refresh token cookie and access token to response
    - logout:
        -> delete cookie that holds the refresh token
        -> delete refresh token from db
"""

from bonham.bonham_auth.handler import activate, login, logout, sign_up
from bonham.bonham_auth.models import *
from bonham.bonham_core.component import Component
from bonham.bonham_core.db import create_tables
from bonham.settings import SUPERUSERS

__all__ = ('Auth', 'authentication_required')

ROUTES = (
    ('POST', r'sign-up/', sign_up, 'sign-up'),
    ('PUT', r'login/', login, 'login'),
    ('PUT', r'logout/', logout, 'logout'),
    ('PUT', r'{activation_key}/', activate, 'activate')
    )

DEFAULT_ROLES = {
    'admin': (1, 1, 1),  # can add, update, delete
    'editor': (1, 1, 0),  # can add and update
    'friend': (1, 0, 0),  # can add
    'follower': (0, 0, 0),  # can't do anything
    'default': (0, 0, 0)  # can't do anything
    }


class Auth(Component):
    r"""Authentication and Authorisation Component"""

    def __init__(self):
        super().__init__()
        self._tables = create_tables(
            models=(
                Account, Role, AccountRole,
                Permission, Client
                )
            )

    @staticmethod
    async def setup_superusers(service):
        """
        Creates superusers in database if they don't already exist
        and adds them to the services _state attribute.

        get superusers from service:
            superusers = service['superusers']

        add admin to service:
            service['superusers'][new_superuser['id']] = new_superuser
        """
        service.logger.debug(f"creating super users")
        service.logger.debug(f"service {vars(service)}")
        service['superusers'] = dict()
        async with service.db.acquire() as connection:
            account = Account(connection)
            superusers = list(await account.get(
                many=True,
                fields=['id', 'email'],
                where=f"is_superuser=True"
                ))
            print(f"superusers: {superusers}")
            if not len(superusers):
                for _superuser in SUPERUSERS:
                    await account.create(
                        data=dict(_superuser)
                        )
                    print(f"created superuser: {account}")
                    service['superusers'][account.id] = dict(id=account.id,
                                                             email=account.email)
            else:
                service.logger.debug(
                    f"\n\tregistered superusers: {list(superusers)}"
                    )
                service['superusers'] = {
                    superuser['id']: dict(
                        id=superuser['id'],
                        email=superuser['email']
                        ) for superuser in superusers
                    }

    @staticmethod
    async def setup_roles_and_permissions(service):
        """
        Creates roles and permissions in database if they don't already exist.

        """
        service.logger.debug(f"creating roles and permissions")
        async with service.db.pool.acquire() as connection:
            for role_name, permissions in DEFAULT_ROLES.items():
                role = Role(connection, name=role_name)
                await role.get(where=f"name='{role_name}'")
                if role.id is None:
                    await role.create()
                for table_name in service['tables']:
                    permission = Permission(
                        connection, role_id=role.id, table_name=table_name,
                        can_add=str(permissions[0]),
                        can_update=str(permissions[1]),
                        can_delete=str(permissions[2]))
                    await permission.get(
                        where=f"role_id={role.id} AND table_name='{table_name}'"
                        )
                    if permission.id is None:
                        await permission.create()

    async def setup(self, service):
        for route in ROUTES:
            service.router.add_route(
                route[0], f'/auth/{route[1]}',
                route[2], name=route[3]
                )

        await self.setup_superusers(service)
        service.db.tables.update(self._tables)
        service['failed_logins'] = {}
        # service._on_startup.append(self.setup_roles_and_permissions)

    async def shutdown(self, service):
        print(f"Authentication shut down!")
