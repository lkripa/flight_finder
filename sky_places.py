import requests, json 
import config
import pandas as pd

class Places():
    def __init__(self):
        self.url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/autosuggest/v1.0/ES/EUR/en-US/"
        self.headers = {
            'x-rapidapi-key': config.api_key,
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
        }
        columns = ['sky_id', 'name', 'region', 'country']
        self.df_places = pd.DataFrame(columns = columns)

    def request_place(self, query):
        try:
            response = requests.request("GET", self.url, headers=self.headers, params=query)
            temp = json.loads(response.text)
            if 'Places' in temp:
                for place in temp['Places']:
                    self.df_places = self.df_places.append({'sky_id': place['PlaceId'], 'name': place['PlaceName'], 'region': place['RegionId'], 'country': place['CountryName']}, ignore_index=True)
            else:
                print('Query doesn\'t match any names')
        except:
            continue

def main(query='London'):

    querystring = {"query":query, "includeAirports":"true"}
    Pl = Places()
    Pl.request_place(querystring)

    #if Pl.df_places.empty:
        # not a country or big enough (# airports >1 ) city
        #querystring = {"query":query, "includeAirports":"true"}
        #Pl = Places()
        #Pl.request_place(querystring)

    #sky_id = Pl.df_places['sky_id'].tolist()
    #print(sky_id)

    return Pl.df_places

if __name__ == '__main__':
    main()