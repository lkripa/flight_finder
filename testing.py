import requests

url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/referral/v1.0/ES/EUR/en-US/ZRH-sky/LAX-sky/2021-05-27/%7Binboundpartialdate%7D"

querystring = {"shortapikey":"ra66933236979928","apiKey":"{shortapikey}"}

headers = {
    'x-rapidapi-key': "084f78c5c5mshf7c49aa2baf9685p1258a0jsnce551a20b861",
    'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)