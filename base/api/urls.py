from django.urls import path
from .views import ListRoomsApiView, RoomApiVIew


urlpatterns = [
    path('rooms/', ListRoomsApiView.as_view(), name='rooms'),
    path('rooms/<str:pk>/', RoomApiVIew.as_view(), name='room-api')
]