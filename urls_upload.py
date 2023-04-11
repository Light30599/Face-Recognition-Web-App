from flask import Blueprint
from flask import render_template, request,abort,flash,redirect,url_for,current_app,session
from jinja2 import TemplateNotFound
import os
#from werkzeug.utils import secure_filename
from validateur_dataset import validateur_dataset
from dataset_creator import DatasetCreator
upload_page = Blueprint('uploads', __name__,template_folder='templates',static_folder='static')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# Allowed file extensions for upload images
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# router for upload images page
@upload_page.route('/',methods=['GET'])
def upload_image():
    if request.method == 'GET':
        return render_template('upload.html')
    else:
        abort(404)

@upload_page.route('/', methods=['POST'])
def upload_file():
	# check if the post request has user information
	session.clear()
	session["id"] = request.form['user_id'].strip()
	session["name"] = request.form['user_name'].strip()
	session["age"] = request.form['user_age'].strip()
	session["gendre"] = request.form['user_gendre'].strip()	
	# validate user information
	errors = validateur_dataset(session["id"],session["name"],session["age"],session["gendre"])
	if (errors):
		for error in errors:
			flash(error,"error")
		return redirect(url_for('uploads.upload_image'))
	# check if the post request has the file part
	if 'files[]' not in request.files:
		flash('No file part', "error")
		return redirect(request.url)
	files = request.files.getlist('files[]')
	file_names = []
	count = 0
	dataset_creator = DatasetCreator(False)
	for file in files:
		if file and allowed_file(file.filename):
			#filename = secure_filename(file.filename)
			#file_names.append(filename)
			# create dataset
			
			#set data for dataset creation
			dataset_creator.set_user_data_age(session["age"])
			dataset_creator.set_user_data_gen(session["gendre"])
			dataset_creator.set_user_data_id(session["id"])
			dataset_creator.set_user_data_name(session["name"])
			Id = dataset_creator.save_data_collection()
			# file name for save image
			count = count + 1
			filename = "User."+str(Id)+"."+str(count)+".jpg"
			file_names.append(filename)
			# save image
			file.save(os.path.join(current_app.config['UPLOAD_FOLDER_UPLOADS'], filename))
		else:
			flash('Allowed image types are -> png, jpg, jpeg, gif','error')
			return redirect(request.url)
	flash('File(s) successfully uploaded','success')
	return render_template('upload.html', filenames=file_names)

@upload_page.route('/display/<filename>', methods=['GET'])
def display_image(filename):
	return redirect(url_for('static', filename='uploads/'+filename), code=301)