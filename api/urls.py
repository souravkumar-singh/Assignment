from django.urls import path
from . import views

urlpatterns = [
    path('', views.new_view),
    path('api/register-user/', views.register_user, name='user-registration'),
    path('api/apply-loan/', views.apply_loan, name='apply-loan'),
    path('api/make-payment/', views.make_payment, name='make-payment'),
    path('api/get-statement/', views.get_statement, name='get-statement'),
]
