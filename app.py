from flask import Flask, jsonify, request, make_response
from setuptools import setup, find_packages
from os import environ
from flask_sqlalchemy import SQLAlchemy
from flask.views import MethodView
from sqlalchemy.orm import clear_mappers

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres-db/delgado_gonzalez'

db= SQLAlchemy(app)

class User (db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    emails = db.Column(db.ARRAY (db.String), nullable=False, unique=True)

    def serialize (self):
        return {
            'id': self.id,
            'name': self.name,
            'emails': list(self.emails)
        }
    
with app.app_context():
    db.create_all()

@app.route('/status/', methods= ['GET'])
def getstatus():
    return jsonify({'response': 'pong'})

@app.route('/directories/', methods= ['GET'])
def getdirectories():
    user = User.query.all()
    serialize_directories = [user.serialize() for user in user]
    response = jsonify (serialize_directories)
    return make_response (response, 200)

@app.route('/directories/', methods= ['POST'])
def postdirectories():
    data = request.get_json()
    name = data.get('name')
    emails = data.get('emails')
    user = User(name=name, emails=emails)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize())

@app.route('/directories/<int:pk>', methods=['GET'])
def get_directory(pk):
    user = User.query.get(pk)
    if user is None:
        return jsonify({'message': 'directory not found'}), 404
    return jsonify(user.serialize())

@app.route('/directories/<int:pk>', methods=['PUT'])
def update_directory(pk):
    user = User.query.get(pk)
    if user is None:
        return jsonify({'message': 'Directory not found'}), 404

    data = request.get_json()
    user.name = data.get('name')
    user.emails = data.get('emails')

    db.session.commit()
    return jsonify(user.serialize())

@app.route('/directories/<int:pk>', methods=['PATCH'])
def partial_update_directory(pk):
    user = User.query.get(pk)
    if user is None:
        return jsonify({'message': 'Directory not found'}), 404

    data = request.get_json()

    if 'name' in data:
        user.name = data['name']
    if 'emails' in data:
        user.emails = data['emails']

    db.session.commit()

    return jsonify(user.serialize())

@app.route('/directories/<int:pk>', methods=['DELETE'])
def delete_directory(pk):
    user = User.query.get(pk)
    if user is None:
        return jsonify({'message': 'Directory no encontrado'}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Directory eliminado'})


if __name__ == '__main__':
    clear_mappers()
    app.run()
