import os
import cv2
import numpy as np
from PIL import Image
from flask import current_app
## trainer.py
#This file trains the algorithm on the dataset that you have created.

# In this setup we are using the LBPHFaceRecognizer_create() method to create a recognizer object.
class Trainer():
    def __init__(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.path = current_app.config['UPLOAD_FOLDER']
        self.image_local_paths = [os.path.join(self.path,f) for f in os.listdir(self.path) if f.endswith('.jpg')]
        self.uploaded_path = current_app.config['UPLOAD_FOLDER_UPLOADS']
        self.image_upload_paths = [os.path.join(self.uploaded_path,f) for f in os.listdir(self.uploaded_path) if os.path.isfile(os.path.join(self.uploaded_path,f))]
        self.image_paths = self.image_local_paths + self.image_upload_paths
        self.faces = []
        self.ids = []

    def get_images_with_ids(self):
        
        for single_image_path in self.image_paths:
            faceImg = Image.open(single_image_path).convert("L")
            faceNp = np.array(faceImg, np.uint8)
            id = int(os.path.split(single_image_path)[-1].split(".")[1])
            print(id)
            self.faces.append(faceNp)
            self.ids.append(id)

        return np.array(self.ids), self.faces
    def process_dataset(self):
        ids, faces = self.get_images_with_ids()
        self.recognizer.train(faces, ids)
        self.recognizer.save("recognizer/my_biometre_data_training.yml")

    # verify data process is done
    def is_dataset_processed(self):
        if os.path.exists("recognizer/my_biometre_data_training.yml"):
            return True
        else:
            # create dataset if not exist
            self.process_dataset()
            return False