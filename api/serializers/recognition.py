from rest_framework import serializers 
from api.models.people import People
 
class RecognitionSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = People
        fields = ('p_id','face')