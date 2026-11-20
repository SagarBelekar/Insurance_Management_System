from django.urls import path
from . import views

urlpatterns = [
    # Landing Page
    path('', views.landing_page, name='landing_page'),

    path('', views.landing_page, name='landing_page'),

    # Public Informational Pages
    path('about/', views.about_page, name='about_page'),
    path('features/', views.features_page, name='features_page'),
    path('contact/', views.contact_page, name='contact_page'),

    # Admin Profile Route
    path('admin-panel/profile/', views.admin_profile_view, name='admin_profile'),

    # User Profile Route
    path('user/profile/', views.user_profile_view, name='user_profile'),

    # User Auth Flow
    path('user-register/', views.user_register_view, name='user_register'),
    path('register/', views.user_register_view, name='register'),  # Backward compatibility

    path('user-login/', views.user_login_view, name='user_login'),
    path('login/', views.user_login_view, name='login'),          # Backward compatibility
    
    # Admin Auth Flow
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),

    # User Dashboard & Operations
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('plans/', views.browse_plans, name='browse_plans'),
    path('buy/<int:plan_id>/', views.buy_policy, name='buy_policy'),
    path('user/my-policies/', views.my_policies, name='my_policies'),
    path('user/submit-claim/<int:policy_id>/', views.submit_claim, name='submit_claim'),
    path('user/claim-status/', views.claim_status, name='claim_status'),

    # Admin Dashboard & Operations
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/claims/', views.manage_claims, name='manage_claims'),
    path('admin-panel/claim/<int:claim_id>/<str:action>/', views.claim_action, name='claim_action'),
    path('admin-panel/plans/', views.manage_plans, name='manage_plans'),
]