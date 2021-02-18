from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from get_data import get_user_params, get_flights
from calculate_cheapest import get_common_dest, save_df_to_json
import config



app = Flask(__name__)
CORS(app)

@app.route('/cityPost', methods=['POST'])
def cityPost():
  message = request.get_json(force=True)
  print(message)
  origin_list = message["input"]
  # main(origin_list)
  show_flight_info=False
  headers = {
  'x-rapidapi-key': config.api_key,
  'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
  }

  print("Processing user-defined parameters...")
  print()
  params, return_trip = get_user_params(origin_list, show_flight_info)

  print("Requesting flight data...")
  df_outbound, df_inbound = get_flights(headers, params, return_trip)
  
  num = len(df_outbound)
  print(f"Number of possible flights to be analyzed: {num}")
  print()
  print("Done!")

  # get common destinations for outbound and inbound trips
  print('OUTBOUND FLIGHTS-------')
  print('Date: ', params['date_outbound'])
  print('Getting common destinations and calculating prices...')
  df_common_dest_outbound = get_common_dest(df_outbound)
  print()
  print('Saving flights to sorted_common_dest.txt')
  save_df_to_json(df_common_dest_outbound, 'Data/sorted_common_dest.json')
  print()
  # print_top_flights(params, df_common_dest_outbound)

  if params['date_inbound'] != None:
      print()
      print('INBOUND FLIGHTS-------')
      print('Date: ', params['date_inbound'])
      print('Getting common destinations and calculating prices...')
      #df_common_dest_inbound = get_common_dest(df_inbound)
      
      # have to figure out how to combine inbound and outbound
      # 

  print()
  print('Done!')

    
  # response = {
  #       'input': message['input']
  #   }
  response = json.load(open('Data/sorted_common_dest.json', 'r'))
  return response

# @app.route('/cityGet', methods=['GET'])
# def cityGet():
#   response = json.load(open('Data/sorted_common_dest.json', 'r'))
#   return response

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