from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser, User
from apps.a12n.utils import async_get_user_from_token

class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get('headers'))
        auth_header = headers.get(b'authorization').decode()

        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
            scope['user'] = await async_get_user_from_token(token) if token else AnonymousUser()

        return await super().__call__(scope, receive, send)