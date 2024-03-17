import os
import json


from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from project import Project, get_projects

app = Flask(__name__)
app.debug = False
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api/project/list', methods=['GET'])
@cross_origin()
def getProjects():
    projects = []
    for p in get_projects():
        projects.append(p.to_obj())
    return jsonify(projects), 200

@app.route('/api/project/create', methods=["POST", "OPTIONS"])
@cross_origin()
def create_project():
    data = request.json
    if not 'name' in data:
        return jsonify({ "Error": "No name provided "}), 200
    name = data["name"]
    if f'{name}.json' in os.listdir('projects'):
        return jsonify({ "Error": "Project name already taken"}), 200
    project = Project(name)
    project.save()
    return jsonify({ "Error": None }), 200

@app.route('/api/project/get', methods=["GET"])
@cross_origin()
def get_project_api():
    try:
        name = request.args.get('id')
        if name is None:
            return jsonify({ "Error": f"Project \"{name}\" not found"})
    except:
        return jsonify({ "Error": "Invalid ID "}), 200
    project = Project(name)
    return jsonify(project.to_obj()), 200

@app.route('/api/paper/create', methods=["POST"])
@cross_origin()
def add_paper_api():
    body = request.json
    if not 'arxiv_id' in body:
        return jsonify({ "Error": "Could not find arxiv id in request body"}), 200
    if not 'project_name' in body:
        return jsonify({ "Error": "Could not find project name in request body"}), 200

    paper_id = body['arxiv_id']
    project_name = body['project_name']
    
    if not f'{project_name}.json' in os.listdir('projects'):
        return jsonify({ "Error": "Could not find project name in project list"}), 200
    
    project = Project(project_name)
    project.add_paper(paper_id)
    project.save()
    return jsonify({ "Error": None }), 200

if __name__ == '__main__':
    app.run(port=4000)