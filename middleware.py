from flask_http_middleware import BaseHTTPMiddleware
from flask import jsonify, redirect
from dataset_creator import DatasetCreator
from trainer import Trainer

class SecureRoutersMiddleware(BaseHTTPMiddleware):
    def __init__(self, secured_routers = []):
        super().__init__()
        self.secured_routers = secured_routers

    def dispatch(self, request, call_next):
        if request.path in self.secured_routers:
            #if request.headers.get("FaceApp-Auth") == "TrustMe":
                #return call_next(request)

            # verify dataset_created is true
            data_create = DatasetCreator()

            if (data_create.is_dataset_created() == False):
                return redirect("/dataset_creation", code=302)
                #return jsonify({"message": "dataset not created"})
                
            
            # verify dataset_processed is true
            trainer = Trainer()
            print("test :",trainer.is_dataset_processed())
            if (trainer.is_dataset_processed() == False):
                return redirect("/trainer", code=302)
                #return jsonify({"message": "dataset not processed"})

            else:
                return call_next(request)
        else:
            return call_next(request)