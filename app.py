from flask import Flask, render_template, Response,request,session,jsonify,redirect,current_app,flash
import cv2
from dataset_creator import DatasetCreator
from trainer import Trainer
from detector import Detector
import os
import sqlite3
from flask import g
from flask_wtf.csrf import CSRFProtect, CSRFError
from database_manager import DataBaseManager

# Load environment variables
from dotenv import load_dotenv

load_dotenv()



#router includes upload
from urls_upload import upload_page

#from flask_session import Session
from flask_http_middleware import MiddlewareManager
from middleware import SecureRoutersMiddleware

# create and configure the app
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False # if set to True, user session will be permanent until they logout
app.config["SESSION_TYPE"] = "filesystem"

# Enable CSRF protection
csrf = CSRFProtect(app)

app.config.from_mapping(
        WTF_CSRF_SECRET_KEY = os.urandom(32),
        #PERMANENT_SESSION_LIFETIME=600,
        TESTING = True,
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024,
        SECRET_KEY = os.getenv('SECRET_KEY',os.urandom(32)) ,#os.urandom(32),
        DATABASE = os.path.join(app.instance_path, os.getenv('FLASK_DATABASE_NAME','FaceBase.db')),
        DATABASE_SCHEMA = os.path.join(app.instance_path, os.getenv('FLASK_DATABASE_SCHEMA','FaceBase.sql')),
        UPLOAD_FOLDER = os.getenv('FLASK_UPLOAD_FOLDER_DATASET','dataSet'),
        UPLOAD_FOLDER_UPLOADS = os.getenv('FLASK_UPLOAD_FOLDER_IMAGES','static/uploads'),
        UPLOAD_RECOGNIZER = os.getenv('FLASK_UPLOAD_RECOGNIZER','recognizer')
    )

def init_db():
    # remove database content
    try:
        with app.app_context():
            database = DataBaseManager()
            db = database.get_db()
            print(current_app.name)
        db.execute("DELETE FROM Peoples;")
        db.commit()
        print("Database content deleted")
    except OSError:
        pass
    # remove files in dataset folder
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # remove files in uploads folder
    for filename in os.listdir(app.config['UPLOAD_FOLDER_UPLOADS']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER_UPLOADS'], filename))
    # remove files in trainer folder
    for filename in os.listdir(app.config['UPLOAD_RECOGNIZER']):
        os.remove(os.path.join(app.config['UPLOAD_RECOGNIZER'], filename))

init_db()


# CSP policy for secure headers 
@app.after_request
def apply_csp(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://use.fontawesome.com https://stackpath.bootstrapcdn.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://use.fontawesome.com https://stackpath.bootstrapcdn.com; font-src 'self' https://cdn.jsdelivr.net https://use.fontawesome.com https://stackpath.bootstrapcdn.com;"
    return response

# XSS policy for secure headers
@app.after_request
def apply_xss(response):
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
# XSS content type for secure headers
@app.after_request
def apply_xcto(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# XFO policy for secure headers
@app.after_request
def apply_xfo(response):
    response.headers["X-Frame-Options"] = "DENY"
    return response

# HSTS policy for secure headers
# prevent MITM attacks
@app.after_request
def apply_hsts(response):
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# handle 404 error
@app.errorhandler(404)
def page_not_found(e):
  #return render_template('404.html',error=str(e)), 404
  return render_template('404.html'), 404

# handle 500 error
@app.errorhandler(500)
def internal_server_error(e):
  return render_template('500.html'), 500

# CSRF error handler
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

# set secured routers
app.wsgi_app = MiddlewareManager(app)
app.wsgi_app.add_middleware(SecureRoutersMiddleware, secured_routers=["/trainer","/detection"])
    
# read image file and convert to bytes
def image_to_bytes(image_path):
    with open(image_path, "rb") as image_file:
        return image_file.read()
    
# handle video streaming from webcam and detect user   
def gen_frames_detection():  # generate frame by frame from camera
    with app.app_context():
        detect_user = Detector()
        print(current_app.name)
    
    while True:
        success, frame = detect_user.detect()
        if not success:
            error_image = image_to_bytes('./images/404-error.jpg')
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + error_image + b'\r\n')
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    del detect_user
#ganerate frames for dataset creation
def gen_frames_process(id,name,age,gendre):  # generate frame by frame from camera
    if (id is None or name is None or age is None or gendre is None):
        error_image = image_to_bytes('./images/404-error.jpg')
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + error_image + b'\r\n')
        return
    with app.app_context():
        data_create = DatasetCreator()
        print(current_app.name)
    #set data for dataset creation
    data_create.set_user_data_age(age)
    data_create.set_user_data_gen(gendre)
    data_create.set_user_data_id(id)
    data_create.set_user_data_name(name)

    Id = data_create.save_data_collection()
    while True:
        success, frame, sampleNum = data_create.handle_frame(Id)
        if not success:
            error_image = image_to_bytes('./images/404-error.jpg')
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + error_image + b'\r\n')
            break
        else:
            if (sampleNum < 20):
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            else:
                completed_image = image_to_bytes('./images/completed.jpg')
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + completed_image + b'\r\n')
                break
    del data_create     

def gen_frames_Training_algorithme():  # generate frame by frame from camera
    with app.app_context():
        trainer_algor = Trainer()
        print(current_app.name)
    trainer_algor.process_dataset()
    completed_image = image_to_bytes('./images/completed.jpg')
    yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + completed_image + b'\r\n')

@app.route('/video_feed')
def video_feed():
    if request.method == 'GET':
        #Video streaming route. Put this in the src attribute of an img tag
        return Response(gen_frames_detection(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Method not allowed"
    
@app.route('/Processing_dataset')
def Processing_dataset():
    if request.method == 'GET':
        if (session.get('id') is None or session.get('name') is None or session.get('age') is None or session.get('gendre') is None):
            session["id"] = session["name"] = session["age"] = session["gendre"] = None
        #Video streaming route. Put this in the src attribute of an img tag
        return Response(gen_frames_process(session["id"],session["name"],session["age"],session["gendre"]), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Method not allowed"
    
@app.route('/Training_algorithme')
def Training_algorithme():
    #Video streaming route. Put this in the src attribute of an img tag
    if request.method == 'GET':
        return Response(gen_frames_Training_algorithme(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Method not allowed"

# Router

# router for home page
@app.route('/')
def index():
    """ Home page. """
    if request.method == 'GET':
        #return "Welcome to face recognition project"
        return render_template('index.html')
    else:
        return "Method not allowed"

# router for detection page
@app.route('/detection')
def detection():
    """Video streaming home page."""
    if request.method == 'GET':
        return render_template('detection.html')
    else:
        return "Method not allowed"

# router dataset creation page
@app.route('/dataset_creation',methods=['POST','GET'])
def dataset_creation():
    form_test_show = True
    if request.method == 'POST':
        session.clear()
        session["id"] = request.form['user_id'].strip()
        session["name"] = request.form['user_name'].strip()
        session["age"] = request.form['user_age'].strip()
        session["gendre"] = request.form['user_gendre'].strip()
        if (session.get('id') is None or session.get('name') is None or session.get('age') is None or session.get('gendre') is None):
            form_test_show = True
            flash("Please fill the form first","warning")
        elif (session['id'].isdigit() == False ):
            session["id"] = None
            form_test_show = True
            flash("Id must be a number","error")
        elif (session['age'].isdigit() == False ):
            session["age"] = None
            form_test_show = True
            flash("Age must be a number","error")
        elif (session['gendre'] not in ['MAN','WOMEN'] ):
            session["gendre"] = None
            form_test_show = True
            flash("Gendre must be a Male/Female/other","error")
        elif (session['name'].isalpha() == False):
            session["name"] = None
            form_test_show = True
            flash("Name must be a string","error")
        
        else:
            form_test_show = False
        
        return render_template('dataset_creation.html',form_test_show=int(form_test_show))
    elif request.method == 'GET':
        if(session.get("id") is None or session.get("name") is None or session.get("age") is None or session.get("gendre") is None):
            """Video streaming home page."""
            flash("Please fill the form first","warning")
            return render_template('dataset_creation.html',form_test_show=int(True))
        return render_template('dataset_creation.html',form_test_show=int(False))
    else:
        return "Method not allowed"
    
# router for trainer page
@app.route('/trainer')
def trainer():
    """Video streaming home page."""
    if request.method == 'GET':
        return render_template('trainer.html')  
    else:
        return "Method not allowed"

# router for upload images page

with app.app_context():
    current_app.register_blueprint(upload_page, url_prefix='/upload')
    print(current_app.name)

if __name__ == '__main__':
    #app.run(debug=True, ssl_context='adhoc')
    app.run(debug=os.getenv('FLASK_DEBUG',True),port=os.getenv('FLASK_RUN_PORT', 5000),host=os.getenv('FLASK_RUN_HOST', '127.0.0.1'))