import os
import re
import cv2
import glob
import csv
import torch
import pandas as pd
import numpy as np
from numpy import asarray
from PIL import Image
from mtcnn.mtcnn import MTCNN
from facenet_pytorch import InceptionResnetV1, MTCNN as MTCNN_FACENET

from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import Http404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from api.models.people import People
from api.serializers.recognition import RecognitionSerializer
from api.utils.lfw import *

class Recognition(APIView):

    def post(self, request, format=None):
        serializer = RecognitionSerializer(data=request.data)
        if serializer.is_valid():
            #check device
            device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
            print('Running on device: {}'.format(device))

            # get image
            img = Image.open(request.data['face'])
            pixels = asarray(img)

            #face detector
            mtcnn = MTCNN()
            detector = mtcnn.detect_faces(pixels)

            if len(detector) == 0:
                return Response({"message": "No Face Detected"}, status=status.HTTP_400_BAD_REQUEST) 

            if len(detector) > 1:
                return Response({"message": "More Than One Face"}, status=status.HTTP_400_BAD_REQUEST)

            # get cropped and prewhitened image tensor
            mtcnn_facenet = MTCNN_FACENET(
                image_size=160, margin=0, min_face_size=20,
                thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
                device=device 
            )
            # embedding
            img_cropped = mtcnn_facenet(img)
            resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
            resnet.classify = True
            embeddings1 = resnet(img_cropped.unsqueeze(0)).detach().cpu()
            # get all image
            basepath = os.getcwd()
            fc = os.path.join(basepath, "data\\lfw\\")
            ext = ['png', 'jpg', 'jpeg', 'gif', 'webp']
            files = []
            [files.extend(glob.glob(fc + '*.' + e)) for e in ext]
            images = [cv2.imread(file) for file in files]
            # distancing embbed
            for imgs in images:
                list_img_cropped = mtcnn_facenet(imgs)
                embeddings2 = resnet(list_img_cropped.unsqueeze(0)).detach().cpu()
                #if embeddings2 is not None:
                    ### bug ####
                    # dist = distance(embeddings1, embeddings2, 1)
                    # print(dist)
            return Response({"message": "Recognition Successfully !"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)