from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
database_uri = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)



class SearchQuery(db.Model):   
    id = db.Column(db.Integer, primary_key=True) 
    school = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False)
    equipment = db.Column(db.String) 
    response= db.Column(db.String)
    incident=db.Column(db.String)
    perception=db.Column(db.String)
    witness=db.Column(db.String)
  

class TextEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    schools=db.Column(db.String, nullable=True)
    situation=db.Column(db.String, nullable=True) 

class ContactEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name=db.Column(db.String(255), nullable=False)
    emails=db.Column(db.String(255), nullable=False)
    message=db.Column(db.String(255), nullable=False)
    school=db.Column(db.String, nullable=True)
@app.route('/api/schools', methods=['GET'])
def get_schools():
    search_query = request.args.get('name', '')  
    if search_query:
    
        schools = SearchQuery.query.filter(SearchQuery.school.ilike(f'%{search_query}%')).with_entities(SearchQuery.school).distinct()
    else:
       
        schools = SearchQuery.query.with_entities(SearchQuery.school).distinct()
    
    return jsonify([school.school for school in schools])


@app.route('/api/saveTextToDatabase', methods=['POST'])
def save_text_to_database():
    try:
        data = request.json
        text_input = data.get('textInput')
        school_input=data.get('schools')
        situation_input=data.get('situation')
 
        text_entry = TextEntry(text=text_input, schools=school_input, situation=situation_input)
        db.session.add(text_entry)
        db.session.commit()

        return jsonify(message="Text saved successfully"), 201
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/save_choice', methods=['POST'])
def save_choice():
    data = request.json
    selected_choice = data.get('equipment', '')  
    selected_choice2=data.get('response', '')
    selected_choice3=data.get("incident", "")
    selected_choice4=data.get("perception", "")
    selected_choice5=data.get("witness", "")
    school_name = data.get('school', 'Unknown School')  
    user_email = data.get('email', 'Unknown Email')   

    if selected_choice or selected_choice2 or selected_choice3 or selected_choice4 or selected_choice5:

        choice = SearchQuery(school=school_name, email=user_email, equipment=selected_choice, response=selected_choice2, incident=selected_choice3, perception=selected_choice4, witness=selected_choice5)
        db.session.add(choice)
        db.session.commit()
        return jsonify(message='Choice saved successfully'), 200
    else:
        return jsonify(message='Invalid data'), 400
    

@app.route('/api/saveContactToDatabase', methods=['POST'])
def save_contact_to_database():
    try:
        print("Received contact save request")  
        data = request.json
        name_input = data.get('name')
        print(name_input)
        emails_input=data.get('emails')
        message_input=data.get('message')   
        school_input=data.get('schools')
        contact_entry = ContactEntry(name=name_input, emails=emails_input, message=message_input, school=school_input )
        db.session.add(contact_entry)
        db.session.commit()

        return jsonify(message="Text saved successfully"), 201
    except Exception as e:
        return jsonify(error=str(e)), 500
