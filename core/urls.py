from django.urls import path

from .views import login, logout, refresh_auth_token

app_name = "core"


urlpatterns = [

    # auth/login/
    path('auth/login/', login, name='sign-in'),

    # auth/logout/
    path('auth/logout/', logout, name='sign-out'),

    # auth/refresh-token/
    path('auth/refresh-token/', refresh_auth_token, name='refresh-token'),
]
