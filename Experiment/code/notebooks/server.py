import random
import os
from flask import Flask, request, jsonify, flash, redirect, url_for, send_from_directory, render_template
from keyword_spotting_service import Keyword_Spotting_Service
from werkzeug.utils import secure_filename
import processor

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = 'wav'

# instantiate flask app
app = Flask(__name__)

# Limit content size
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/accueil/')
def index():
    return render_template('index.html')

@app.route('/recherche/')
def recherche():
    return render_template('recherche.html')

# Upload files function
@app.route('/indexe/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'],
                secure_filename(file.filename))
            file.save(filename)
            return redirect(url_for('predict',
                filename=filename))
    return render_template("indexe.html")

#méthode pour la prédiction
@app.route("/predict", methods=["GET"])
def predict():
	"""Endpoint to predict keyword

    :return (json): This endpoint returns a json file with the following format:
        {
            "keyword": "waaw"
        }
	"""

	# get file from POST request and save it
	#audio_file = request.files["file"]
	#file_name = str(random.randint(0, 100000))
	#random.randint(a, b) renvoie un entier aléatoire N tel que a <= N <= b et La fonction str convertit des données en chaîne
	#audio_file.save(file_name)
	file_name = request.args['filename']
	# instantiate keyword spotting service singleton and get prediction
	kss = Keyword_Spotting_Service()
	predicted_keyword = kss.predict(file_name)

	# we don't need the audio file any more - let's delete it!
	os.remove(file_name)

	# send back result as a json file
	result = {"keyword": predicted_keyword}
	return render_template("autotest.html", predictions_to_render=result['keyword']) if predicted_keyword=="waaw" else render_template("indexe.html", predictions_to_render=result['keyword'])

#gestion des résultats
@app.route('/chat/', methods=["GET", "POST"])
def chatbot():
    return render_template('chatbot.html', **locals())



@app.route('/chatbot', methods=["GET", "POST"])
def chatbotResponse():

    if request.method == 'POST':
        the_question = request.form['question']

        response = processor.chatbot_response(the_question)

    return jsonify({"response": response })


if __name__ == "__main__":
    app.run(debug=False)


