import requests, json
import sys
import time
import re
import pandas as pd
from tqdm import tqdm
from config_api import get_key


# TODO: handle inbound legs - for now only doing specific airports so limits the return flights,
#       check for valid currencies

def match_skyscanner(city_list, table):
    """
    Match user-defined cities (or countries) with corresponding IDs required by Skyscanner API
    :param city_list: list of city names, provided by the user from dropdown of city_user 
                      ex. [London (GB),Boston (US)]
    Returns all IDs of all airports that serve that city
    """
    city_id = []
    # table = pd.read_csv('Data/city_codes.csv')

    for city in city_list:
        city_id.append(list( table.loc[table['city_user'] == city, 'iata_sky_code'] ))
    
    city_id_list = [city for sub_city in city_id for city in sub_city]

    return city_id_list

def assign_city_names(airport_iata_code, table):
    """
    Return corresponding city serviced by airport

    :param airport_iata_code: str, airtport ID

    """
    # table = pd.read_csv('Data/city_codes.csv')
    city_name = table.loc[table['iata_code'] == airport_iata_code, 'city'].item()

    return city_name

def user_input():
    """
    Define user preferences FROM PYTHON
    Return user parameters for get_params()
    """
    # ask user for data and match with names in database
    while True:
        origin_list = (input('Please provide the two origin cities - ex. Madrid (ES),Paris(FR) : ')).split(',')
        destination_list = (input('Please provide the possible destination - ex. London (GB) : ')).split(',')
        
        # removes a space if one is accidentally added
        if len(origin_list) > 1 and origin_list[1][0] == " ":
            origin_list[1] = origin_list[1][1:]
        # checks for correct string formatting
        rex = re.compile("^[A-Z][a-z]*\s{1}[(][A-Z]{2}[)]$")
        try:
            if rex.match(origin_list[0]) and rex.match(origin_list[1]) and rex.match(destination_list[0]):
                print("Correct format")
            else:
                raise TypeError("Wrong string format")
            break
        except TypeError:
            print()
            print('The city provided is not in the correct format! Take a look at the example. Please try again: ')
    while True:
        date_outbound = input('Please provide the desired outbound date (yyyy-mm-dd): ')
        rex = re.compile("^202[1-9][-][0-1][0-9][-][0-3][0-9]$")
        try:
            if rex.match(date_outbound):
                print("Correct format")
            else:
                raise TypeError("Wrong date format")
            break
        except TypeError:
            print()
            print('Invalid Date. Please try again: ')
    num_flights = input('How many flights would you like to see? (ex. enter 3 to see top 3 cheapest flights) ')
    return origin_list, destination_list, date_outbound, num_flights

def get_params(origin_list, destination_list, date_outbound, num_flights, table, show_flight_info):
    """
    Define user preferences from python or webapp
    Return dict of parameters, and return_trip to indicate whether one-way or round-trip

    app.py sends arguments here by saved user queries from webapp
    """
    #default
    return_trip = False

    # ask user for data and match with names in database
    
    # while True:
    # try:
    origin_list_ids = (match_skyscanner(origin_list, table))
        
    # except:
    #     print()
    #     print('The names provided don\'t match any cities or countries! Please try again: ')

    # while True:
    # try:
    destination_list_ids = match_skyscanner(destination_list, table)
    # except:
    #     print()
        # print('The names provided don\'t match any cities or countries! Please try again: ')  
    
    # date_inbound = input('Please provide the desired inbound date (yyyy-mm-dd), or enter a space if only one-way trip: ')
    
    date_inbound = ' '
    if date_inbound == ' ':
        date_inbound = None
    else:
        return_trip = True
        print('       return trip confirmed!')
    
    print()

    params = {
        'origin' : origin_list_ids,
        'origin_country' : 'ES',
        'destination' : destination_list_ids,
        'currency': 'EUR',
        'locale': 'en-US',
        'date_outbound' : date_outbound,
        'date_inbound' : date_inbound,
        'num_flights' : num_flights,
        'root_url': "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/",
        'show_flight_info': show_flight_info
        }

    return params, return_trip

def pause_API():
    """
    API Rate Limit: 50 per minute (unlimited requests)
    Create a pause to allow all the calls to go through.
    """
    print("-----------")
    print("-----------")
    print("PAUSED")
    print("-----------")
    print("-----------")
    time.sleep(60)

def get_flights(headers, params, table, return_trip):
    """
    Skyscanner API request for every origin and destination provided by user
        Rate Limit: 50 per minute (unlimited requests)

    Then extracts relevant info from API request, i.e. match airport IDs from Skyscanner 
        API with their respective names to get inbound and outbound flight info

    :param headers: credentials, provided by RapidAPI
    :param params: user's preferences
    :param return_trip: indicates whether one-way or round-trip flight

    Returns dataframe of outbound and inbound flight info, including airport IDs, city names,
            carrier names, and total price of journey
    """
    beginning = time.perf_counter()
    airport_ID = {}
    carrier_ID = {}
    currency = params['currency']

    columns = ['origin_sky_id', 'origin_iata_id', 'dest_sky_id', 'dest_iata_id', 'price', 'carrier','date']
    df_outbound = pd.DataFrame(columns = columns)
    df_inbound = pd.DataFrame(columns = columns)

    print('Processing flight data...', end="\n\n")
    count = 0
    stop1 = time.perf_counter()
    # print(f"get_flights setup in {stop1 - beginning:0.4f} seconds")
    
    #! Delay is here ~5 secs
    for origin in tqdm(params['origin']):
        stop2 = time.perf_counter()
        print(f"get_flights after API FOR--{origin}-- {stop2 - stop1:0.4f} seconds")
        for destination in params['destination']:
            stop3 = time.perf_counter()
            print(f"    get_flights after API TO: {destination} {stop3 - stop2:0.4f} seconds")
            try:
                count += 1
                # Pause API request because of Basic account limit
                #! ERROR This will cause a problem if temp gets activated under 50
                if count % 50 == 0:
                    pause_API()
                    
                # print("-----------Request from API---------------", count)
                # API request - Browse Flight Searches
                myurl = params['root_url'] + params['origin_country'] + "/" + params['currency'] + "/" + params['locale'] + "/"  + \
                    origin + "/" + destination + "/" + params['date_outbound']

                # if return_trip:
                    #querystring = {"inboundpartialdate" : params['date_inbound']}
                    #r = requests.request("GET", myurl, headers=headers, params=querystring)
                    # myurl += '/' + params["date_inbound"]
                print(myurl)
                r = requests.request("GET", myurl, headers=headers)
                print(r.text)
                temp = json.loads(r.text)
                if temp == {'message': 'You have exceeded the rate limit per minute for your plan, BASIC, by the API provider'}:
                    pause_API()
                # stop4 = time.perf_counter()
                # print(f"      API CALL: {stop4 - stop3:0.4f} seconds")
                print(temp)
                # Extract relevant flight info
                # build dicts with IDs (int) : IATA codes of airports or names of carriers
                
                for places in temp["Places"]:
                    airport_ID[places["PlaceId"]] = places["IataCode"] 
                
                for carrier in temp["Carriers"]:
                    carrier_ID[carrier["CarrierId"]] = carrier["Name"]
                
                # stop5 = time.perf_counter()
                # print(f"      2 For-Loops for Carrier and Places: {stop5 - stop4:0.4f} seconds")
                # assign route info (with matched names) to outbound and inbound lists
                if "Quotes" in temp: 
                    for quotes in temp["Quotes"]:
                        # access data returned
                        origin_outbound = quotes["OutboundLeg"]["OriginId"]                     
                        carrier_outbound = quotes["OutboundLeg"]["CarrierIds"] #list of IDs,int
                        dest_outbound = quotes["OutboundLeg"]["DestinationId"]
                        price = quotes["MinPrice"]
                        whole_date = quotes["OutboundLeg"]["DepartureDate"].split("T")
                        date = whole_date[0]

                        # match to IDs
                        origin_iata_id = airport_ID[origin_outbound]
                        origin_sky_id = origin_iata_id + '-sky'
                        dest_iata_id = airport_ID[dest_outbound]
                        dest_sky_id = dest_iata_id + '-sky'
                        carrier_name = carrier_ID[carrier_outbound[0]]

                        df_outbound = df_outbound.append({'origin_sky_id': origin_sky_id, 'origin_iata_id': origin_iata_id, \
                             'dest_sky_id':dest_sky_id, 'dest_iata_id':dest_iata_id, 'price':price, \
                                'carrier': carrier_name, 'date': date}, ignore_index=True)
                        
                        if return_trip:
                            origin_inbound = quotes["InboundLeg"]["OriginId"]
                            dest_inbound = quotes["InboundLeg"]["DestinationId"]
                            carrier_inbound = quotes["InboundLeg"]["CarrierIds"]
                            # date_inbound = quotes["InboundLeg"]["DepartureDate"]

                            origin_iata_id = airport_ID[origin_inbound]
                            origin_sky_id = origin_iata_id + '-sky'
                            dest_iata_id = airport_ID[dest_inbound]
                            dest_sky_id = dest_iata_id + '-sky'
                            carrier_name = carrier_ID[carrier_inbound[0]]

                            df_inbound = df_inbound.append({'origin_sky_id': origin_sky_id, 'origin_iata_id': origin_iata_id, \
                                'dest_sky_id':dest_sky_id, 'dest_iata_id':dest_iata_id, 'price':price, \
                                    'carrier': carrier_name, 'date': date}, ignore_index=True)

                        if params['show_flight_info']:
                            print("-----------")
                            print(f"Outbound Journey: {airport_ID[origin_outbound]}  --> {airport_ID[dest_outbound]}")
                            print(f"Carrier: {carrier_ID[carrier_outbound[0]]}")
                            print()
                            if return_trip:
                                print(f"Inbound Journey:  {airport_ID[origin_inbound]}  --> {airport_ID[dest_inbound]}")
                                print(f"Carrier: {carrier_ID[carrier_inbound[0]]}")     
                                print()         
                            print(f"Total price: {price} {currency}")
                # stop6 = time.perf_counter()
                # print(f"      Create df_outbound: {stop6 - stop5:0.4f} seconds")
            except:
                # airport is not in Skyscanner database
                # ideally can get a database of valid skyscanner airports and further filter the city_codes table with it
                continue
    
    stop7 = time.perf_counter()
    print(f"get_flights after API in:== beginning of get_flights to end of for-loops== {stop7 - beginning:0.4f} seconds")
    start = time.perf_counter()
    # add corresponding city names to dataframes
    try:
        df_outbound['origin_city_name'] = df_outbound.apply(lambda row: assign_city_names(row['origin_iata_id'], table), axis=1)
        df_outbound['dest_city_name'] = df_outbound.apply(lambda row: assign_city_names(row['dest_iata_id'], table), axis=1)

        if return_trip:
            df_inbound['origin_city_name'] = df_inbound.apply(lambda row: assign_city_names(row['origin_iata_id'], table), axis=1)
            df_inbound['dest_city_name'] = df_inbound.apply(lambda row: assign_city_names(row['dest_iata_id'], table), axis=1)
    except Exception as error:
        print('Origin City Not Found: ')
        print("     Exception Error:",error)
    stop = time.perf_counter()
    print(f"get_flights after API in when creating df_outbound {stop - start:0.4f} seconds")
    print(f"get_flights from beginning in {stop - beginning:0.4f} seconds")
    return df_outbound, df_inbound


def main(show_flight_info=False):
    table = pd.read_csv('Data/city_codes.csv')
    # -- Uncomment to hard-code --
    # origin_list = ["Madrid (ES)", "Zurich (CH)"]
    # destination_list = ['London (GB)']
    # date_outbound = "2021-04-01"
    # num_flights = 3
    # -- Comment to hard-code --
    origin_list, destination_list, date_outbound, num_flights = user_input()
    
    headers = {
    'x-rapidapi-key': get_key(),
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
    }

    print("Processing user-defined parameters...", end="\n\n")
    params, return_trip = get_params(origin_list, destination_list, date_outbound, num_flights, table, show_flight_info)

    print("Requesting flight data...", end="\n\n")
    df_outbound, df_inbound = get_flights(headers, params, table, return_trip)
    
    num = len(df_outbound)
    print(f"Number of possible flights to be analyzed: {num}")
    print("Done!")

    return params, df_outbound, df_inbound


if __name__ == "__main__":
    main()
