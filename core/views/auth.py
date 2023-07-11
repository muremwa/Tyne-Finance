from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes

from core.models import User
from core.serializers import UserSerializer


@api_view(['POST'])
@permission_classes([])
def login(request):
    """
        Accepts POST request with data: username, password.
            { 'username': string, 'password': string }
        returns user data and token
    """
    resp = {'message': 'username and password required', 'success': False}
    status_code = status.HTTP_400_BAD_REQUEST

    if username := request.data.get('username'):
        if password := request.data.get('password'):
            authenticated_user: User | None = authenticate(username=username, password=password)

            if authenticated_user:
                authenticated_user.last_login = timezone.now()
                authenticated_user.save()
                status_code = status.HTTP_200_OK
                resp.update({
                    'message': 'user found',
                    'success': True,
                    'token': authenticated_user.get_user_auth_token().key,
                    'user': UserSerializer(authenticated_user).data
                })

            else:
                resp.update({'message': 'Incorrect username or password'})
                status_code = status.HTTP_401_UNAUTHORIZED

    return JsonResponse(resp, status=status_code)


@api_view(['POST'])
def logout(request):
    """
        User token is nullified
    """
    request.auth.delete()
    return JsonResponse({'success': True}, status=status.HTTP_200_OK)


@api_view(['POST'])
def refresh_auth_token(request):
    """New token is returned"""
    request.auth.delete()

    return JsonResponse({
        'token': Token.objects.create(user=request.user).key
    }, status=status.HTTP_200_OK)
