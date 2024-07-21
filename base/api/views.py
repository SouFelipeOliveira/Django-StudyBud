from rest_framework.views import APIView
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer


class ListRoomsApiView(APIView):
    """
    return a rooms list
    """
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)


class RoomApiVIew(APIView):  # noqa: F811
    """
    Return a unique room
    """
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        serializer = RoomSerializer(room, many=False)
        return Response(serializer.data)