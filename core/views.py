from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.utils import timezone

from .models import User
from .serializers import UserSerializer


@api_view(['POST'])
@permission_classes([])
def login(request):
    resp = {'message': 'username and password required', 'success': False}
    status_code = status.HTTP_400_BAD_REQUEST

    if username := request.data.get('username'):
        if password := request.data.get('password'):
            authenticated_user: User | None = authenticate(username=username, password=password)

            if authenticated_user:
                if authenticated_user.is_active:
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
                    resp.update({'message': 'User is not active'})
                    status_code = status.HTTP_403_FORBIDDEN

            else:
                resp.update({'message': 'Incorrect username or password'})
                status_code = status.HTTP_403_FORBIDDEN

    return JsonResponse(resp, status=status_code)


@api_view(['POST'])
def logout(request):
    request.auth.delete()
    return JsonResponse({'success': True}, status=status.HTTP_200_OK)


@api_view(['POST'])
def refresh_auth_token(request):
    request.auth.delete()

    return JsonResponse({
        'token': Token.objects.create(user=request.user).key
    }, status=status.HTTP_200_OK)
