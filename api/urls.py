from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.controllers.people import *
from api.controllers.register import Register
from api.controllers.recognition import Recognition
 
urlpatterns = [ 
    path('people', PeopleList.as_view()),
    path('people/<int:pk>', PeopleDetail.as_view()),
    path('register', Register.as_view()),
    path('recognition', Recognition.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)