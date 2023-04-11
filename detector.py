import cv2
import numpy as np
import os
from database_manager import DataBaseManager
from flask import current_app

## detector.py
#This file detects your face and when detected show the result
class Detector(DataBaseManager):
    def __init__(self):
        self.facedetect = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.path_recognizer_model = os.path.join(current_app.config['UPLOAD_RECOGNIZER'], 'my_biometre_data_training.yml')
        self.recognizer.read(self.path_recognizer_model)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.cam = cv2.VideoCapture(0)
        super().__init__()
        self.conn = super().get_db()


    def getProfile(self,id):
        cursor = self.conn.execute("SELECT id,Name,Age,Gender FROM Peoples WHERE id=?", (id,))
        profile=None
        for row in cursor:
            profile=row
        return profile
    
    def detect(self):
        ret,img=self.cam.read()
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces=self.facedetect.detectMultiScale(gray,1.3,5)
        for(x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            id,conf=self.recognizer.predict(gray[y:y+h,x:x+w])
            profile=self.getProfile(id)
            print(profile)
            if(profile != None):
                cv2.putText(img, "Name : "+str(profile[1]), (x,y+h+25),cv2.FONT_HERSHEY_COMPLEX, 1,(0,255,127),2)
                cv2.putText(img, "Age : "+str(profile[2]), (x,y+h+50),cv2.FONT_HERSHEY_COMPLEX, 1,(0,255,127),2)
                cv2.putText(img, "Gender : "+str(profile[3]), (x,y+h+75),cv2.FONT_HERSHEY_COMPLEX, 1,(0,255,127),2)
        return ret,img
        #cv2.imshow("Face",img)
        #if(cv2.waitKey(1)==ord('q')):
            #break
    def __del__(self):
        self.conn.close()
        self.cam.release()
        #cv2.destroyAllWindows()
