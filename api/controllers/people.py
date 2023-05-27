from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404

from api.models.people import People
from api.serializers.people import PeopleSerializer

class PeopleList(APIView):

    # list all
    def get(self, request, format=None):
        people = People.objects.all()
        serializer = PeopleSerializer(people, many=True)
        return Response(serializer.data)

    # create
    def post(self, request, format=None):
        serializer = PeopleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PeopleDetail(APIView):

    # get object
    def get_object(self, pk):
        try:
            return People.objects.get(pk=pk)
        except People.DoesNotExist:
            raise Http404

    # get one
    def get(self, request, pk, format=None):
        people = self.get_object(pk)
        serializer = PeopleSerializer(people)
        return Response(serializer.data)

    # update
    def put(self, request, pk, format=None):
        people = self.get_object(pk)
        serializer = PeopleSerializer(people, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # remove
    def delete(self, request, pk, format=None):
        people = self.get_object(pk)
        people.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)