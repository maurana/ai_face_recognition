from rest_framework import serializers 
from api.models.people import People
 
class PeopleSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = People
        fields = ('p_id','name','face')