from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models.people import People
from api.serializers.people import PeopleSerializer

@api_view(['POST'])
async def register(self, request, format=None):

@api_view(['POST'])
async def recognition(self, request, format=None):