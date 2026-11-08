from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path('',views.index,name='index'),
    path('register/', views.register_user, name='register'),
    path('login/',views.login,name='login'),
    path('about/', views.about, name='about'),
    path("logout/", logout_view, name="logout"),
    path('admin_index/',views.admin_index,name='admin_index'),
    path('user_index/',views.user_index,name='user_index'),
    path("add-category/", views.add_category, name="add_category"),

    path('update_category/<int:id>/', update_category, name='update_category'),
    path('delete_category/<int:id>/', delete_category, name='delete_category'),
    path("add-outfit/", views.add_outfit, name="add_outfit"),
    path("user_view_outfit/", views.user_view_outfit, name="user_view_outfit"),
    path('outfit_details/<int:outfit_id>/', views.outfit_details, name='outfit_details'),
    path('delete_outfit/<int:outfit_id>/', delete_outfit, name='delete_outfit'),
    path('edit_outfit/<int:outfit_id>/', edit_outfit, name='edit_outfit'),
    path('user_view_outfit_details/<int:outfit_id>/', views.user_view_outfit_details, name='user_view_outfit_details'),
    


    # path('outfits/', view_outfits, name='view_outfits'),
    path('admin_view_outfit/', admin_view_outfit, name='admin_view_outfit'),
    path('orders/', admin_view_orders, name='admin_orders'),
    path('orders/<int:order_id>/payment/', view_payment_details, name='view_payment_details'),

    
    # path('book_outfit/<int:outfit_id>/', book_outfit, name='book_outfit'),
    # path('payment/<int:booking_id>/', payment, name='payment'),
    path('admin_notifications/', admin_notifications, name='admin_notifications'),
    # path('success_booking/<int:booking_id>/', success_booking, name='success_booking'),
    path('my_orders/', my_orders, name='my_orders'),

    path('book_outfit/<int:outfit_id>/', book_outfit, name='book_outfit'),
    path('payment/<int:booking_id>/', payment, name='payment'),
    path('success_booking/<int:booking_id>/', success_booking, name='success_booking'),


    path('profile/',        views.view_profile,   name='view_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

    path('feedback/<int:booking_id>/', views.add_feedback, name='add_feedback'),


    path('wishlist/',                      views.view_wishlist,   name='view_wishlist'),
    path('wishlist/toggle/<int:outfit_id>/', views.toggle_wishlist, name='toggle_wishlist'),


    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    path('admin-users/', views.admin_view_users, name='admin_view_users'),
    path('block-user/<int:id>/', views.block_user, name='block_user'),
    path('unblock-user/<int:id>/', views.unblock_user, name='unblock_user'),
]

