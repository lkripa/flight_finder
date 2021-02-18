from flask import Flask, request, jsonify
from flask_cors import CORS
import json


app = Flask(__name__)
CORS(app)

@app.route('/cityPost', methods=['POST'])
def cityPost():
  message = request.get_json(force=True)
  print(message)
  origin_list = message["input"]
  response = {
        'input': message['input']
    }
  return jsonify(response)

@app.route('/cityGet', methods=['GET'])
def cityGet():
  response = json.load(open('Data/sorted_common_dest.json', 'r'))
  return response

# @app.route('/testpost', methods=['POST'])
# def testpost(message):
#     response = {
#         'input': message['input'],
#         'output': 'result depending on input',
#     }
#     return jsonify(response)

# @app.route('/testget', methods=['GET'])
# def testget():
#     response = {
#         'output': 'getting some stuff',
#     }
#     return jsonify(response)