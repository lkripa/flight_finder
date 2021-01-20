import requests, json
import sys
import pandas as pd

def match_skyscanner(city_list):
    """
    Match user-defined cities (or countries) with corresponding IDs required by Skyscanner API

    :param city_list: city name (or country), provided by the user
    
    Returns Skyscanner API's corresponding ID
    """
    city_id = []

    # load database, for now as a csv 8kb
    db_names =  pd.read_csv('SkyscannerAPIplaces.csv', sep=',')

    # look up ID for each item in list
    for city in city_list:
        clean_city = city.lower().replace('-', ' ').replace('.', '')
        clean_city = " ".join(clean_city.split())
        city_id.append(db_names.loc[db_names['Name'] == clean_city, 'ID'].iloc[0])

    return city_id

def get_user_params():
    """
    Define user preferences 

    Return dict of parameters, and return_trip to indicate whether one-way or round-trip
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
    
    # TODO: some checks for valid dates, ex format / after today
    date_outbound = input('Please provide the desired outbound date (yyyy-mm-dd): ')
    #date_inbound = input('Please provide the desired inbound date (yyyy-mm-dd): ')
    print()

    params = {
        'origin' : origin_list_ids,
        'origin_country' : 'ES',
        'destination' : destination_list_ids,
        'currency': 'EUR',
        'locale': 'en-US',
        'date_outbound' : date_outbound,
        'date_inbound' : None,
        'root_url': "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/",
        'show_flight_info': False
        }
    
    if params['date_inbound'] != None:
        return_trip = True
    
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

    Returns list of outbound and inbound flight info, including airport names, 
            carrier names, and total price of journey
    """
    airport_ID = {}
    carrier_ID = {}
    outbound = []
    inbound = []

    for origin in params['origin']:
        for destination in params['destination']:

            # API request
            myurl = params['root_url'] + params['origin_country'] + "/" + params['currency'] + "/" + params['locale'] + "/"  + \
                origin + "/" + destination + "/" + params['date_outbound']

            if return_trip:
                #querystring = {"inboundpartialdate" : params['date_inbound']}
                #r = requests.request("GET", myurl, headers=headers, params=querystring)
                myurl += '/' + params["date_inbound"]
            
            r = requests.request("GET", myurl, headers=headers)
            temp = json.loads(r.text)

            
            #if "Quotes" in temp: 

            # Extract relevant flight info
            # build dicts with IDs and Names of airports and carriers
            for places in temp["Places"]:
                airport_ID[places["PlaceId"]] = places["Name"] 
            
            for carrier in temp["Carriers"]:
                carrier_ID[carrier["CarrierId"]] = carrier["Name"]
            
            # assign route info (with matched names) to outbound and inbound lists
            for quotes in temp["Quotes"]:
                origin_outbound = quotes["OutboundLeg"]["OriginId"] #int
                carrier_outbound = quotes["OutboundLeg"]["CarrierIds"] #list of IDs,int
                dest_outbound = quotes["OutboundLeg"]["DestinationId"] #int
                price = quotes["MinPrice"] #int

                outbound.append({"origin": airport_ID[origin_outbound], "destination": airport_ID[dest_outbound], \
                    "carrier": carrier_ID[carrier_outbound[0]], "price": price})

                if return_trip:
                    origin_inbound = quotes["InboundLeg"]["OriginId"]
                    dest_inbound = quotes["InboundLeg"]["DestinationId"]
                    carrier_inbound = quotes["InboundLeg"]["CarrierIds"]
                    
                    inbound.append({"origin": airport_ID[origin_inbound], "destination": airport_ID[dest_inbound], \
                        "carrier": carrier_ID[carrier_inbound[0]]})

                if params['show_flight_info']:
                    print("-----------")
                    print(f"Outbound Journey: {airport_ID[origin_outbound]}  --> {airport_ID[dest_outbound]}")
                    print(f"Carrier: {carrier_ID[carrier_outbound[0]]}")
                    print()
                    if return_trip:
                        print(f"Inbound Journey:  {airport_ID[origin_inbound]}  --> {airport_ID[dest_inbound]}")
                        print(f"Carrier: {carrier_ID[carrier_inbound[0]]}")     
                        print()         
                    print(f"Total price: {price} EUR")
                
    return outbound, inbound


def main():
    headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': "a25c140655mshcc3de02bc48e78fp1d8ae5jsn716b89dc608a"
        }

    print("Processing user-defined parameters...")
    print()
    params, return_trip = get_user_params()

    print("Requesting flight data...")
    outbound, inbound = get_flights(headers, params, return_trip)
    
    num = len(outbound)
    print(f"Number of possible flights to be analyzed: {num}")

    print("Done!")


if __name__ == "__main__":
    main()



