from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.controllers.people import *
 
urlpatterns = [ 
    path('people', PeopleList.as_view()),
    path('people/<int:pk>', PeopleDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)