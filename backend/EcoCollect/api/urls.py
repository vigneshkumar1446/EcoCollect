from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    register_user,
    WasteCategoryViewset,
    PickupRequestViewset,
    RecyclerAssignmentViewSet,
    RatingViewSet,
    get_profile,
    NotificationViewSet,
    user_dashboard,
    recycler_rating_stats,
    ChatboxViewSet,
    ChatroomViewSet,
    recycler_pickup_history,
    admin_dashboard,
    admin_manage_users,
    admin_update_user,
    mark_notifications_read,
)

router = DefaultRouter()

router.register('categories', WasteCategoryViewset)
router.register('pickups', PickupRequestViewset)
router.register('assignments', RecyclerAssignmentViewSet)
router.register('rating',RatingViewSet)
router.register('notifications', NotificationViewSet,basename='notification')
router.register('chatrooms', ChatroomViewSet, basename='chatrooms')
router.register('messages', ChatboxViewSet, basename='messages')


urlpatterns = [
    path('register/', register_user),
    path('profile/',get_profile),
    path('dashboard/', user_dashboard),
    path('recycler-rating/', recycler_rating_stats),
    path("recycler-history/", recycler_pickup_history),
    path("admin-dashboard/", admin_dashboard),
    path("admin-users/", admin_manage_users),
    path("admin-users/<int:user_id>/", admin_update_user),
    path("notifications/read/",mark_notifications_read),
    path('', include(router.urls)),
]