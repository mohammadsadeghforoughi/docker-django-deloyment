from django.urls import path

from account.views import logout_view, register_view, SignView

urlpatterns = [path('login/', SignView.as_view(), name='login'),
               path('logout/', logout_view, name='logout'),
               path('register/', register_view, name='register'), ]
