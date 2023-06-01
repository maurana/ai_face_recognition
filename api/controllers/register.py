import os
import re
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
from api.models.people import People
from api.serializers.people import PeopleSerializer

class Register(APIView):

    def post(self, request, format=None):
        serializer = PeopleSerializer(data=request.data)
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

            obj = serializer.save()

            basepath = os.getcwd()
            file_name = str(re.sub(r"\s+", "", obj.name.lower())) + '-' + str(obj.p_id)
            dir2 = "data\\lfw\\"
            fc2 = os.path.join(basepath,dir2,file_name+'.jpg')

            # embedding
            img_cropped = mtcnn_facenet(img, save_path=fc2)
            resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
            resnet.classify = True
            img_probs = resnet(img_cropped.unsqueeze(0)).detach().cpu()

            # save tensor to csv
            t = torch.tensor(img_probs)
            t_np = t.numpy()
            df = pd.DataFrame(t_np)
            fc = os.path.join(basepath, "media/csv", file_name+'.csv')
            df.to_csv(fc,index=False)
            
            return Response({"message": "Registration Successfully !"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)