**Flight Finder**

## Context and Goal
Amid the pandemic still racing through the world in early 2021, I've found myself missing one of the simple pleasures in life I could afford to partake in pre-COVID : traveling. 

The goal of this project is to **find the optimal (in this case, cheapest) common flight destination between two origins**. Say you work in Zürich, and want to plan a trip with a friend who lives in Madrid: how can you find the cheapest destination in the South of France where you both can fly to? A lot of the work behind such a process usually involves iterative requests and comparisons, so why not build an app that automatically takes care of that given the parameters (ie. dates, origins, possible destinations..) provided by the web app user and serves for ex the top 3 cheapest options?

## Run locally
1. Clone this repo
2. Run `$python calculate_cheapest.py`. You will be prompted to provide two user cities, possible destination cities that you wish to consider, outbound and inbound flight dates, and number of flights (ranked in order of total price) to display

## Files
* `get_data.py` : processes user input and corresponding API request
* `calculate_cheapest.py` : computes total cost for all common city destinations and displays ranked results
* `Data/city_iata.db` : database of cities, airports, geolocation, and corresponding IATA codes
* `Data/city_codes.zip` and `Data/city_codes.csv` : table of relevant flight info from above database, with additional Skyscanner IDs

## Steps
1. Use [datahub.io's](https://datahub.io/core/airport-codes) `airport-codes` dataset, includes airport names, cities, IATA_codes, and geolocation (lat & long)
2. Create new SQLLite database, load above dataset, and create new table with relevant fields
```SQL
SELECT municipality AS city_name, iso_country AS country, iso_region AS region, name AS airport_name, latitude_deg, longitude_deg, iata_code
FROM airports
WHERE iata_code IS NOT NULL  AND city_name IS NOT NULL
ORDER BY country, region
```
3. Load table with SQLAlchemy and add additional required field, such as Skyscanner's IATA IDs (`city_codes.csv`)
4. Get flight parameters from user (cities, dates...), and match cities and destinations to `city_codes.csv` entries
5. Run GET request from Skyscanner API's BrowseQuotes endpoint with user parameters using Skyscanner's IATA IDs retrieved in previous step
6. Parse results for relevant data (i.e. airport names, cities, carriers, and prices)
7. Match common city destination options and save to dataframe
8. Rank options according to total price from two origins


