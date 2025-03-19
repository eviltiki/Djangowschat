from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from apps.accounts.services.user_creator import UserCreator


@database_sync_to_async
def async_get_user_from_token(token):
    try:
        validated_token = AccessToken(token)

        if validated_token:
            user_id = validated_token['user_id']
            return UserCreator(user_id).get()
        else:
            return AnonymousUser()
    except (InvalidToken, TokenError):
        return AnonymousUser()