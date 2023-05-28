import os
import re
import csv
import torch
import pandas as pd
import numpy as np
from numpy import asarray
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import datasets
from mtcnn.mtcnn import MTCNN
from facenet_pytorch import InceptionResnetV1, MTCNN as MTCNN_PYTORCH

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from api.models.people import People
from api.serializers.people import PeopleSerializer

class Recognition(APIView):

    def post(self, request, format=None):
        return NULL