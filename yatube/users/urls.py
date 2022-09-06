from django.contrib.auth import views as views_auth
from django.urls import path

from . import views

app_name = 'users'


urlpatterns = [
    # Регистрация
    path('signup/',
         views.SignUp.as_view(
             template_name='users/signup.html'
         ),
         name='signup'),

    # Войти
    path('login/',
         views_auth.LoginView.as_view(
             template_name='users/login.html'
         ),
         name='login'),

    # Выйти
    path('logout/',
         views_auth.LogoutView.as_view(
             template_name='users/logout.html'
         ),
         name='logout'),

    # Смена пароля: задать новый пароль
    path('password_change/',
         views_auth.PasswordChangeView.as_view(
             template_name='users/password_change_form.html'
         ),
         name='password_change'),

    # Смена пароля: Уведомление об удачной смене пароля
    path('password_change/done/',
         views_auth.PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'
         ),
         name='password_change_done'),

    # Восстановление пароля: форма восстановления через email
    path('password_reset/',
         views_auth.PasswordResetView.as_view(
             template_name='users/password_reset_form.html'
         ),
         name='password_reset'),

    # Восстановление пароля: уведомление об отправке ссылки через email
    path('password_reset/done/',
         views_auth.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),

    # Восстановление пароля: подтверждение сброса. По ссылке из почты!
    path('reset/<uidb64>/<token>/',
         views_auth.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ),
         name='reset_confirm'),

    # Восстановление пароля: уведомление, что пароль изменен
    path('reset/done/',
         views_auth.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='reset_done'),
]
