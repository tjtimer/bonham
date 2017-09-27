from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest

from bonham.bonham_auth.functions import check_password, check_retries
from bonham.bonham_auth.models import Account, Client
from bonham.bonham_auth.token import create_token
from bonham.bonham_core.decorators import db_connection, load_data


@load_data
@db_connection
async def login(request: web.Request) -> web.json_response:
    """login
    flow:
        - read email from data
        - check retries
            -> refuse request if user failed to log in more than:
                - 3 times in 90 seconds
                - more than 20 times in 60 minutes
        - get account data from db by given email
        - check password
            -> if password is wrong
                - refuse request
                - add email-address, user agent and timestamp to failed logins
        - update account data (set is_logged_in to True and save to db)
        - create access, bearer and refresh token
        - save refresh and bearer token to db
        - create json response from success message
        - add access and refresh token to response.headers
        - add bearer token cookie to response.cookies
        - return response

    ---
    description: Login endpoint
    tags:
    - Authentication
    responses:
        "200 OK":
            description:
                returns welcome back message
                and client settings
            headers:
                Cookie-Set:
                    description: holding bearer cookie
                    type: string
                Access-Token:
                    description: holding access token
                    type: string
                Refresh-Token:
                    description: holding refresh token
                    type: string
    """
    try:
        data = request['data']
        assert all(key in data.keys()
                   for key in ['email', 'password']), 'email and password ' \
                                                      'must be provided'
        await check_retries(
            data['email'], request.app['failed_logins']
            )
        user_agent = request.headers.get('User-Agent', 'no-ua')
        host = request.headers.get('Host', 'no-host')
        account = Account(request['db_connection'])
        client = Client(request['db_connection'])
        await account.get(
            where=f"email='{data['email']}'",
            returning=['id', 'email', 'password', 'created']
            )
        if account.id is None:
            raise HTTPBadRequest(
                body=f"Account {data['email']} does not exist"
                )
        await check_password(request, account.password)
        await client.get(
            where=f"owner={account.id} "
                  f"AND host='{host}' "
                  f"AND user_agent='{user_agent}'"
                )
        if client.id is None:
            bearer_token_payload = dict(
                id=account.id,
                clientId=f"{account.id}@{host}-"
                         f"{user_agent}"
                )
            bearer_token = await create_token('bearer', bearer_token_payload)
            await client.create(
                data=dict(
                    owner=account.id,
                    host=host,
                    user_agent=user_agent,
                    token=bearer_token
                    )
                )
        access_token_payload = dict(
            id=account.id,
            email=account.email,
            locale=account.locale,
            idc=account['created'],
            cbt=client.token
            )
        access_token = await create_token('access', access_token_payload)
        response = web.json_response(
            dict(
                message=f"welcome back {account.email}",
                client_settings=client.settings),
            headers=dict(access=access_token)
                )
        max_age = 2400 * 3600  # 100 days
        response.set_cookie(
            'bearer', client.token,
            max_age=max_age, secure=True, httponly=True
            )
        return response
    except AssertionError as ae:

        return web.json_response(
            dict(error=f"{ae}"),
            status=405
            )

    except KeyError as ke:

        raise HTTPBadRequest(text=f"Request must provide {ke}.")
