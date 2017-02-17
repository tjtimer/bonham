from aiohttp import web

from bonham.bonham_user.handler import delete_user, get_friends, get_user, get_users, request_friendship, update_user


def setup_routes(router):
    router.add_get(r'/', get_users, name='get-users')
    router.add_get(r'/{id}/', get_user, name='get-user')
    router.add_put(r'/{id}/', update_user, name='update-user')
    router.add_delete(r'/{id}/', delete_user, name='delete-user')

    router.add_get(r'/{user_id}/friends/', get_friends, name='get-friends')
    router.add_post(r'/{user_id}/friends/{id}/', request_friendship, name='request-friendship')


app = web.Application()
setup_routes(app.router)
