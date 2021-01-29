import requests, json
import sys
import pandas as pd
from tqdm import tqdm

# TODO: handle inbound legs - for now only doing specific airports so limits the return flights,
#       check for valid currencies,
#       offer date range for inbound and outbound (vs specific dates)

def match_skyscanner(city_list):
    """
    Match user-defined cities (or countries) with corresponding IDs required by Skyscanner API
    :param city_list: list of city names, provided by the user from dropdown of city_user 
                      ex. [London (GB), Boston (US)]
    Returns all IDs of all airports that serve that city
    """
    city_id = []
    table = pd.read_csv('Data/city_codes.csv')

    for city in city_list:
        city_id.append(list( table.loc[table['city_user'] == city, 'iata_sky_code'] ))
    
    city_id_list = [city for sub_city in city_id for city in sub_city]

    return city_id_list

def assign_city_names(airport_iata_code):
    """
    Return corresponding city serviced by airport

    :param airport_iata_code: str, airtport ID

    """
    table = pd.read_csv('Data/city_codes.csv')
    city_name = table.loc[table['iata_code'] == airport_iata_code, 'city'].item()

    return city_name

def get_user_params(show_flight_info):
    """
    Define user preferences
    Return dict of parameters, and return_trip to indicate whether one-way or round-trip

    once we set up front-end: would use get_user_params (origin_list, destination_list, date_outbound, date_inbound)
    with those arguments provided by saved user queries from webapp
    """
    #default
    return_trip = False

    # ask user for data and match with names in database
    while True:
        origin_list = (input('Please provide the two origin cities (separated by a comma): ')).split(',')
        try:
            origin_list_ids = match_skyscanner(origin_list)
            break
        except:
            print()
            print('The names provided don\'t match any cities or countries! Please try again: ')

    while True:
        destination_list = (input('Please provide possible destinations (separated by a comma): ')).split(',')
        try:
            destination_list_ids = match_skyscanner(destination_list)
            break
        except:
            print('The names provided don\'t match any cities or countries! Please try again: ')  
    
    date_outbound = input('Please provide the desired outbound date (yyyy-mm-dd): ')
    date_inbound = input('Please provide the desired inbound date (yyyy-mm-dd), or enter a space if only one-way trip: ')
    if date_inbound == ' ':
        date_inbound = None
    else:
        return_trip = True
        print('       return trip confirmed!')
    num_flights = input('How many flights would you like to see? (ex enter 3 to see top 3 cheapest flights) ')

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

def get_flights(headers, params, return_trip):
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
    airport_ID = {}
    carrier_ID = {}
    currency = params['currency']

    columns = ['origin_sky_id', 'origin_iata_id', 'dest_sky_id', 'dest_iata_id', 'price', 'carrier']
    df_outbound = pd.DataFrame(columns = columns)
    df_inbound = pd.DataFrame(columns = columns)

    print()
    print('Processing flight data...')
    for origin in tqdm(params['origin']):
        for destination in params['destination']:

            try:
                # API request - Browse Flight Searches
                myurl = params['root_url'] + params['origin_country'] + "/" + params['currency'] + "/" + params['locale'] + "/"  + \
                    origin + "/" + destination + "/" + params['date_outbound']

                if return_trip:
                    #querystring = {"inboundpartialdate" : params['date_inbound']}
                    #r = requests.request("GET", myurl, headers=headers, params=querystring)
                    myurl += '/' + params["date_inbound"]
                
                r = requests.request("GET", myurl, headers=headers)
                temp = json.loads(r.text)

                # Extract relevant flight info
                # build dicts with IDs (int) : IATA codes of airports or names of carriers
                for places in temp["Places"]:
                    airport_ID[places["PlaceId"]] = places["IataCode"] 
                
                for carrier in temp["Carriers"]:
                    carrier_ID[carrier["CarrierId"]] = carrier["Name"]
                
                # assign route info (with matched names) to outbound and inbound lists
                if "Quotes" in temp: 
                    for quotes in temp["Quotes"]:
                        # access data returned
                        origin_outbound = quotes["OutboundLeg"]["OriginId"]                     
                        carrier_outbound = quotes["OutboundLeg"]["CarrierIds"] #list of IDs,int
                        dest_outbound = quotes["OutboundLeg"]["DestinationId"]
                        price = quotes["MinPrice"]

                        # match to IDs
                        origin_iata_id = airport_ID[origin_outbound]
                        origin_sky_id = origin_iata_id + '-sky'
                        dest_iata_id = airport_ID[dest_outbound]
                        dest_sky_id = dest_iata_id + '-sky'
                        carrier_name = carrier_ID[carrier_outbound[0]]

                        df_outbound = df_outbound.append({'origin_sky_id': origin_sky_id, 'origin_iata_id': origin_iata_id, \
                            'dest_sky_id':dest_sky_id, 'dest_iata_id':dest_iata_id, 'price':price, \
                                'carrier': carrier_name}, ignore_index=True)

                        if return_trip:
                            origin_inbound = quotes["InboundLeg"]["OriginId"]
                            dest_inbound = quotes["InboundLeg"]["DestinationId"]
                            carrier_inbound = quotes["InboundLeg"]["CarrierIds"]

                            origin_iata_id = airport_ID[origin_inbound]
                            origin_sky_id = origin_iata_id + '-sky'
                            dest_iata_id = airport_ID[dest_inbound]
                            dest_sky_id = dest_iata_id + '-sky'
                            carrier_name = carrier_ID[carrier_inbound[0]]

                            df_inbound = df_inbound.append({'origin_sky_id': origin_sky_id, 'origin_iata_id': origin_iata_id, \
                                'dest_sky_id':dest_sky_id, 'dest_iata_id':dest_iata_id, 'price':price, \
                                    'carrier': carrier_name}, ignore_index=True)

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

            except:
                # airport is not in Skyscanner database
                # ideally can get a database of valid skyscanner airports and further filter the city_codes table with it
                continue
    
    # add corresponding city names to dataframes
    df_outbound['origin_city_name'] = df_outbound.apply(lambda row: assign_city_names(row['origin_iata_id']), axis=1)
    df_outbound['dest_city_name'] = df_outbound.apply(lambda row: assign_city_names(row['dest_iata_id']), axis=1)

    if return_trip:
        df_inbound['origin_city_name'] = df_inbound.apply(lambda row: assign_city_names(row['origin_iata_id']), axis=1)
        df_inbound['dest_city_name'] = df_inbound.apply(lambda row: assign_city_names(row['dest_iata_id']), axis=1)
                
    return df_outbound, df_inbound


def main(show_flight_info=False):
    headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': "a25c140655mshcc3de02bc48e78fp1d8ae5jsn716b89dc608a"
        }

    print("Processing user-defined parameters...")
    print()
    params, return_trip = get_user_params(show_flight_info)

    print("Requesting flight data...")
    df_outbound, df_inbound = get_flights(headers, params, return_trip)
    
    num = len(df_outbound)
    print(f"Number of possible flights to be analyzed: {num}")
    print()
    print("Done!")

    return params, df_outbound, df_inbound


if __name__ == "__main__":
    main()
