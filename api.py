import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import uuid
from flask import request, flash, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField,FileAllowed
db = SQLAlchemy()

basedir = os.path.abspath(os.path.dirname(__file__))
accepted_schools = ["Stevenson", "Harvard", "MIT", "Stanford", "Yale", "Lehigh", "UCLA"]
class SearchQuery(db.Model):   
    id = db.Column(db.Integer, primary_key=True) 
    school = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False)
    equipment = db.Column(db.String) 
    response= db.Column(db.String)
app = Flask(__name__)

    
database_uri = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri


db.init_app(app)
migrate = Migrate(app, db)
CORS(app)
@app.route('/hello')
def hello():
    return 'Hello, World!'

@app.route('/api/time', methods=["GET"])
def get_current_time():
    return jsonify({'time': time.time()})

@app.route('/api/schools', methods=['GET'])
def get_schools():
    search_query = request.args.get('name', '')  
    if search_query:
    
        schools = SearchQuery.query.filter(SearchQuery.school.ilike(f'%{search_query}%')).with_entities(SearchQuery.school).distinct()
    else:
       
        schools = SearchQuery.query.with_entities(SearchQuery.school).distinct()
    
    return jsonify([school.school for school in schools])





@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    school_name = data.get('school')
    user_email = data.get('email')
    equipment = data.get('equipment')
    selected_option = data.get('selectedOption')
    user_input = data.get('user_input')

    if school_name not in accepted_schools:
        return jsonify({"error": "School not found"}), 404


    new_submission = SearchQuery(school=school_name, email=user_email, equipment=selected_option, response=user_input)
    db.session.add(new_submission)
    db.session.commit()

    return jsonify({"message": "Submission successful"}), 200

@app.route('/api/submit-survey-response', methods=['POST'])
def submit_survey_response():
    data = request.json
    school_name = data.get('school')
    equipment = data.get('equipment') 
    response = data.get('response')  
    print(f"Received data - School: {school_name}, Equipment: {equipment}, Response: {response}")    
    if school_name not in accepted_schools:
        return jsonify({"error": "School not found"}), 404

    # Save all the data to the database
    search_query = SearchQuery(school=school_name, equipment=equipment,  response=response)
    db.session.add(search_query)
    db.session.commit()

    return jsonify({"message": "Survey response submission successful"}), 200
class TextEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)

@app.route('/api/saveTextToDatabase', methods=['POST'])
def save_text_to_database():
    try:
        data = request.json
        text_input = data.get('textInput')


        text_entry = TextEntry(text=text_input)
        db.session.add(text_entry)
        db.session.commit()

        return jsonify(message="Text saved successfully"), 201
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/save_choice', methods=['POST'])
def save_choice():
    data = request.json
    selected_choice = data.get('equipment', '')  # Default to an empty string if not provided

    # Optional: Handle missing school and email gracefully
    school_name = data.get('school', 'Unknown School')  # Provide a default value
    user_email = data.get('email', 'Unknown Email')    # Provide a default value

    if selected_choice:
        # Create a new Choice object and save it to the database
        choice = SearchQuery(school=school_name, email=user_email, equipment=selected_choice)
        db.session.add(choice)
        db.session.commit()
        return jsonify(message='Choice saved successfully'), 200
    else:
        return jsonify(message='Invalid data'), 400