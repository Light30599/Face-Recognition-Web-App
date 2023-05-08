import cv2
import numpy as np
from database_manager import DataBaseManager
from flask import current_app
import os


## dataset_creator.py: 
#This file will create a initial dataset for you. Just like when your face is scanned when every time you register your face in a smartphone.
class DatasetCreator(DataBaseManager):
    def __init__(self,static=True):
        if (static == True):
            self.faceDetect = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')
            self.cam = cv2.VideoCapture(0)
        self.static = static
        super().__init__()
        self.conn= super().get_db()
        self.sampleNum=0
        self.user_gendre = None
        self.user_name = None
        self.user_age = None
        self.user_id = None
        self.DATASET = current_app.config['UPLOAD_FOLDER']
        self.UPLOADS_DATASET = current_app.config['UPLOAD_FOLDER_UPLOADS']

    def insertOrUpdate(self,Id,Name,Age,Gen):
        cmd="SELECT * FROM Peoples WHERE ID="+str(Id)
        cursor= self.conn.execute(cmd)
        isRecordExist=0
        for row in cursor:
            isRecordExist=1
        if(isRecordExist==1):
            self.conn.execute("UPDATE Peoples SET Name=? WHERE id=?", (Name,Id,))
            self.conn.execute("UPDATE Peoples SET Age=? WHERE id=?",(Age, Id))
            self.conn.execute("UPDATE Peoples SET Gender=? WHERE id=?", (Gen,Id,))
        else:
            self.conn.execute("INSERT INTO Peoples(id,Name,Age,Gender) Values(?,?,?,?)", (Id, Name, Age, Gen))
        self.conn.commit()
        #self.conn.close()

    def get_user_data(self):
        if (self.user_name == None):
            self.user_name = input('Enter User Name:')
        if (self.user_age == None):
            self.user_age = input('Enter User Age:')
        if (self.user_id == None):
            self.user_id = input('Enter User Id:')
        if (self.user_gendre == None):
            self.user_gendre = input("Enter User Gender:")
        return self.user_id,self.user_name,self.user_age,self.user_gendre
    
    def set_user_data_name(self,name):
        self.user_name=name
    def set_user_data_age(self,age):
        self.user_age=age
    def set_user_data_gen(self,gen):
        self.user_gendre=gen
    def set_user_data_id(self,Id):
        self.user_id=Id

    def save_data_collection(self):
        Id,name,age,gen=self.get_user_data()
        self.insertOrUpdate(Id,name,age,gen)
        return Id
       
    def handle_frame(self,Id):
        ret,img=self.cam.read()
        gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces=self.faceDetect.detectMultiScale(gray,1.3,5)
        for(x,y,w,h) in faces:
            self.sampleNum=self.sampleNum+1
            path_data = os.path.join(self.DATASET, "User."+str(Id)+"."+str(self.sampleNum)+".jpg")
            cv2.imwrite(path_data,gray[y:y+h,x:x+w])
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.waitKey(100)
        cv2.putText(
            img, #numpy array on which text is written
            "Process: {value}%".format(value=self.sampleNum), #text
            (20,40), #position at which writing has to start
            cv2.FONT_HERSHEY_SIMPLEX, #font family
            0.7, #font size
            (209, 80, 0, 255), #font color
        3)
        #cv2.imshow("Face",img)
        #cv2.waitKey(1)
        
        return ret,img,self.sampleNum
    def __del__(self):
        if (self.static == True):
            self.cam.release()
            cv2.destroyAllWindows()
        self.conn.close()
    
    # verfify database is not empty
    def is_database_is_not_empty(self):
        cmd="SELECT * FROM Peoples"
        cursor= self.conn.execute(cmd)
        isRecordExist=0
        for row in cursor:
            isRecordExist=1
        if(isRecordExist==1):
            return True
        else:
            return False

    # verify folder is not empty
    def is_folder_empty(self):
        import os
        path = self.DATASET
        path_upload = self.UPLOADS_DATASET
        return (len([os.path.join(path,f) for f in os.listdir(path) if f.endswith('.jpg')]) == 0) and ([os.path.join(path_upload,f) for f in os.listdir(path_upload) if os.path.isfile(os.path.join(path_upload,f))] == 0)

    # verify dataset is created
    def is_dataset_created(self):
        if (self.is_database_is_not_empty() == True and self.is_folder_empty() == False):
            return True
        else:
            return False