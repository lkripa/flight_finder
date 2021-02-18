**Flight Finder**

## Context and Goal
Amid the pandemic still racing through the world in early 2021, I've found myself missing one of the simple pleasures in life I could afford to partake in pre-COVID : traveling. 

Say you work in Zürich, and want to plan a trip with a friend who lives in Madrid: how can you find the cheapest destination in the South of France where you both can fly to? A lot of the work behind such a process usually involves iterative requests and comparisons, so why not build an app that automatically takes care of that given the parameters (ie. dates, origins, possible destinations..) provided by the web app user and serves for ex the top 3 cheapest options?

The goal of this project is to **find the optimal (in this case, cheapest) common flight destination between two origins**. 

*For the webapp, check out [this repo](https://github.com/lkripa/project_neptune) with Lara's front-end work, and the progress so far [here](https://projectneptune-167d5.web.app/)!*

## Run locally
1. Clone this repo
2. Set up  Environment 
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
3. Run `$python calculate_cheapest.py`. You will be prompted to provide two user cities, possible destination cities that you wish to consider, outbound and inbound flight dates, and number of flights (ranked in order of total price) to display
  * Note: You'll have to provide your personal [RapidAPI key](https://rapidapi.com/skyscanner/api/skyscanner-flight-search) (free!). Once you have one, assign `api_key` in a separate `config.py` file. 

## Files
* `get_data.py` : processes user input and corresponding API request
* `calculate_cheapest.py` : computes total cost for all common city destinations and displays ranked results
* `Data/city_iata.db` : database of cities, airports, geolocation, and corresponding IATA codes
* `Data/city_codes.zip` and `Data/city_codes.csv` : table of relevant flight info from above database, with additional Skyscanner IDs

## Steps
1. Use [datahub.io's](https://datahub.io/core/airport-codes) `airport-codes` dataset, includes airport names, cities, IATA_codes, and geolocation (lat & long)
2. Create new SQLLite database, load above dataset, and create new table with relevant fields
```SQL
SELECT name AS airport_name,  latitude_deg, longitude_deg, iso_country AS country, iso_region AS region, municipality AS city, iata_code, iata_code ||  '-sky' AS iata_sky_code, municipality || ' (' || iso_country || ')' AS city_user
FROM airports
WHERE iata_code IS NOT NULL  AND city IS NOT NULL
ORDER BY country, region
```
Available Airports:

![Available Airports](airports.png)

3. Load table with SQLAlchemy, additionally save as csv (`city_codes.csv`)
4. Get flight parameters from user (cities, dates...), and match cities and destinations to `city_codes.csv` entries
5. Run GET request from [Skyscanner API's](https://skyscanner.github.io/slate/#api-documentation) BrowseQuotes endpoint (through [RapidAPI](https://rapidapi.com/skyscanner/api/skyscanner-flight-search?endpoint=5aa1eab3e4b00687d3574279)) with user parameters using Skyscanner's IATA IDs retrieved in previous step
6. Parse results for relevant data (i.e. airport names, cities, carriers, and prices)
7. Match common city destination options and save to dataframe
8. Rank options according to total price from two origins


