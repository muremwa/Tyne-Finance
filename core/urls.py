from django.urls import path

from .views import auth

app_name = "core"


urlpatterns = [

    # auth/login/
    path('auth/login/', auth.login, name='sign-in'),

    # auth/logout/
    path('auth/logout/', auth.logout, name='sign-out'),

    # auth/refresh-token/
    path('auth/refresh-token/', auth.refresh_auth_token, name='refresh-token'),

    # auth/sign-up/
    path('auth/sign-up/', auth.sign_up, name='sign-up'),
]
