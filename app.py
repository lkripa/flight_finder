from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
import pandas as pd
import json
import time
from get_data import get_params, get_flights
from config_api import get_key
from calculate_cheapest import get_common_dest, save_df_to_json


app = Flask(__name__)
CORS(app)
table = pd.read_csv('Data/city_codes.csv')

@app.route('/test', methods=['GET'])
def test():
  response = {
    'test': 'successful',
  }
  return jsonify(response)

@app.route('/cityPost', methods=['POST'])
def cityPost():
  message = request.get_json(force=True)
  print("==============================")
  # -- Arguments here --
  origin_list = message["inputOriginCities"]
  destination_list = message["inputDestinationCity"]
  print(origin_list, destination_list)
  date_outbound = 'anytime'
  num_flights = 3
  show_flight_info = False
  headers = {
    'x-rapidapi-key': get_key(),
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
  }

  print("Processing user-defined parameters...")
  
  start = time.perf_counter()
  params, return_trip = get_params(origin_list, destination_list, date_outbound, num_flights, table, show_flight_info)

  print("Requesting flight data...")
  df_outbound, df_inbound = get_flights(headers, params, table, return_trip)
  
  marker1 = time.perf_counter()
  #! Here is the time suckers
  print(f"  marker 1 from beginning in {marker1 - start:0.4f} seconds")
  num = len(df_outbound)
  print(f"Number of possible flights to be analyzed: {num}", end="\n\n")
  
  if num != 0:
    # get common destinations for outbound and inbound trips
    print('OUTBOUND FLIGHTS-------')
    print('Date: ', params['date_outbound'])
    print('Getting common destinations and calculating prices...')
    marker2 = time.perf_counter()
    df_common_dest_outbound = get_common_dest(df_outbound)
    marker3 = time.perf_counter()
    print(f"  marker 2-3 in {marker3 - marker2:0.4f} seconds")

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

    stop = time.perf_counter()
    print(f"cityPost from beginning in {stop - start:0.4f} seconds", end="\n\n")
  
    print('Done!')
    print("==============================")
    
    # sending to React
    response = json.load(open('Data/sorted_common_dest.json', 'r'))
    
  else:
    print("Blank json sent to react")
    # Uncomment when API is back online
    # sending to React
    response = {}
    # response = json.load(open('Data/sorted_common_dest.json', 'r'))

  return response

if __name__ == '__main__':
  app.run(debug=False, host='0.0.0.0', port=int(environ.get('PORT', 8080)))