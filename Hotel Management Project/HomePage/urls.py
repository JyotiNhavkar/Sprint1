from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from HomePage import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('',views.home, name="home"),
    path('register', views.register, name="register"),
    path('login/',views.login_view,name="login"),
    path('booking_page', views.booking_page, name='booking'),
    path('detail/<str:selected_room_type>/', views.detail_page, name='detail'),
    #path('contact/', contact_us, name='contact_us'),
    path('billing_page/<int:booking_id>/', views.billing_page, name='billing_page'),
    path('confirm_booking/', views.confirm_room, name='confirm_booking'),
    path('service-selection/', views.service_selection, name='service_selection'),
    path('about', views.about, name='about'),
    path('afterlogin/',views.after_login,name="after_login"),
    #path('service-selection/<int:service_id>/', views.service_selection, name='service_detail'),
    path('book-service/<int:booking_id>/', views.book_service, name='book_service'),
    path('staff/', views.staff_viewer, name='Staff_Viewer'),  # Define the URL pattern for staff viewer
    path('dashboard/', views.dashboard, name="dashboard"),
    path('change-password/', auth_views.PasswordChangeView.as_view(), name='passwordChange'),
    path('accounts/login/', lambda request: redirect('/login/')),
    path('change-password/', auth_views.PasswordChangeView.as_view(success_url='/change-password-done/'), name='change_password'),
    path('change-password-done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('profileChange/', views.profileChange, name='profileChange'),
    path('logoutview', views.logoutview, name='logoutview'),
    path('regComplete', views.regComplete, name='regComplete'),
    path('checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('incorrectDetails', views.incorrectDetails, name='incorrectDetails'),
    path('billing/<int:booking_id>/', views.billing_page, name='billing_page'),
    path('receipt/<int:booking_id>/', views.receipt, name='receipt'),
    path('download-receipt/<int:billing_id>/', views.download_receipt, name='download_receipt'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('thankyou/', views.feedback_thankyou, name='feedback_thankyou'),

]
