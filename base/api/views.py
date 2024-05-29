from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import Room
from .serializers import Roomserializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /',
        'GET /rooms',
        'GET /room:id'

    ]
    return Response(routes)


@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serialized_rooms = Roomserializer(rooms, many=True)
    print(serialized_rooms)

    return Response(serialized_rooms.data)


@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serialized_room = Roomserializer(room, many=False)
    print(serialized_room)

    return Response(serialized_room.data)