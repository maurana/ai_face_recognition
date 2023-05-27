from rest_framework import serializers 
from api.models import People
 
class PeopleSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = People
        fields = ('id','name','face')