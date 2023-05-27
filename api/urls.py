from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views 
 
urlpatterns = [ 
    path('people', views.PeopleList.as_view()),
    path('people/<int:pk>', views.PeopleDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)