from django.urls import re_path
from .views import CustomLoginView, CustomLogoutView, CustomSettingsView, CustomSignupView

app_name = 'hasker_user'
urlpatterns = [
    re_path(r'^login/$', CustomLoginView.as_view(), name='login'),
    re_path(r'^logout/$', CustomLogoutView.as_view(), name='logout'),
    re_path(r'^settings/$', CustomSettingsView.as_view(), name='settings'),
    re_path(r'^signup/$', CustomSignupView.as_view(), name='signup'),
]
