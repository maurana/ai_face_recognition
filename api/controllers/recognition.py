import os
import re
import cv2
import math
import glob
import csv
import torch
import pandas as pd
import numpy as np
from numpy import asarray
from PIL import Image
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
from api.serializers.recognition import RecognitionSerializer

class Recognition(APIView):

    def distance(embeddings1, embeddings2, distance_metric=0):
        if distance_metric==0:
            # Euclidian distance
            diff = np.subtract(embeddings1, embeddings2)
            dist = np.sum(np.square(diff),1)
        elif distance_metric==1:
            # Cosine similarity
            dot = np.sum(np.multiply(embeddings1, embeddings2), axis=1)
            norm = np.linalg.norm(embeddings1, axis=1) * np.linalg.norm(embeddings2, axis=1)
            similarity = dot / norm
            dist = np.arccos(similarity) / math.pi
        else:
            raise 'Undefined distance metric %d' % distance_metric 
            
        return dist

    def post(self, request, format=None):
        serializer = RecognitionSerializer(data=request.data)
        if serializer.is_valid():
            #check device
            device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
            print('Running on device: {}'.format(device))

            # get image
            img = Image.open(request.data['face'])
            pixels = asarray(img)
            _got = np.ndarray(img)
            tfn = torch.from_numpy(_got)

            #face detector
            mtcnn = MTCNN()
            detector = mtcnn.detect_faces(pixels)

            if len(detector) == 0:
                return Response({"message": "No Face Detected"}, status=status.HTTP_400_BAD_REQUEST) 

            if len(detector) > 1:
                return Response({"message": "More Than One Face"}, status=status.HTTP_400_BAD_REQUEST)

            # get cropped and prewhitened image tensor
            mtcnn_pytorch = MTCNN_PYTORCH(
                image_size=160, margin=0, min_face_size=20,
                thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
                device=device 
            )

            # embedding
            img_cropped = mtcnn_pytorch(tfn)
            resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
            resnet.classify = True
            img_probs = resnet(img_cropped.unsqueeze(0))

            # get all image
            basepath = os.getcwd()
            fc = os.path.join(basepath, "media\\face\\")
            ext = ['png', 'jpg', 'jpeg', 'gif']
            files = []
            [files.extend(glob.glob(fc + '*.' + e)) for e in ext]
            images = [cv2.imread(file) for file in files]
            images = torch.from_numpy(np.ndarray(images))

            # distancing embbed
            aligned = []
            for imgs in images:
                align, list_img_cropped = mtcnn_pytorch(imgs, return_prob=True)
                list_probs = resnet(list_img_cropped.unsqueeze(0))
                if list_probs is not None:
                    aligned.append(align)
                    dist = self.distance(img_probs, list_probs, 2)
                    print('Image probability: {:8f}'.format(list_img_cropped))
                    print(dist)

            # aligned = torch.stack(aligned).to(device)
            # embeddings = resnet(aligned).detach().cpu()

            
            
            return Response({"message": "Recognition Successfully !"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)