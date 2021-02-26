import get_data
import pandas as pd
import numpy as np
import json


# TODO: 
#       * extend beyond 2 origin cities?
#       * figure out how to combine with return flight

''' 
    Ideas for Frontend:
    They can pick two start origin and an end destination, the dates and price comes out in a popup!
'''


def get_common_dest(df):
    """
    Compares all flights for common destinations between origins and calculates total price

    :param df: dataframe (df_outbound or df_inbound) from which to select common destinations

    Returns dataframe for all common destinations with respective origins and total price of 
    each flight, sorted according to total price
    """
    isFirst = True

    origin_cities = df['origin_city_name'].unique()
    all_dates = df['date'].unique()
    # print("testingtesting", origin_cities)
    for i in range(len(all_dates)):
        df_byDate = (df[ df.date == all_dates[i] ]).reset_index(drop=True)
        # list of flights dfs by origin
        df_origin_list = []
        for city in origin_cities:
            # possible flights per origin
            # df_byOrigin = (df[ df.origin_city_name == city ]).reset_index(drop=True)
            df_byOrigin = (df_byDate[ df_byDate.origin_city_name == city ]).reset_index(drop=True)
            df_origin_list.append(df_byOrigin)
        
        try: 
            # assuming 2 origin cities
            city_name_1 = (df_origin_list[0].dest_city_name.to_numpy())[:, np.newaxis]
            city_name_2 = (df_origin_list[1].dest_city_name.to_numpy())[np.newaxis, :]

            ind = pd.DataFrame(np.argwhere(np.equal(city_name_1, city_name_2)), \
                columns=['ind1', 'ind2'])

            df_common_dest = ind.merge(df_origin_list[0], left_on='ind1', right_index=True).\
                merge(df_origin_list[1],
                left_on='ind2', right_index=True, suffixes=['_1', '_2'])

            df_common_dest.drop(columns=['ind1', 'ind2'], inplace=True)
            
            # add total price col
            df_common_dest['total_price'] = df_common_dest['price_1'] + df_common_dest['price_2']

            # sort by total price (least to most)
            df_common_dest = df_common_dest.sort_values(['total_price']).reset_index(drop=True)
           # print(df_common_dest)
            if isFirst:
                df_main = df_common_dest.copy(deep=True)
                # df_first = df_common_dest.copy(deep=True)
                # print("df_main FIRST",df_main)
                isFirst = False
            if not df_common_dest.empty:
                # print()
               # print('=========')
               # print("Date: ", all_dates[i],' #',i,'/',len(all_dates))
                df_main = df_main.append(df_common_dest, ignore_index=True)
                # df_first = df_main.append(df_common_dest.first("1"), ignore_index=True)
               # print("df_main", df_main)
               # print('=========')
        except IndexError: 
            print("No common destination with this date found - look at city input")
    # sort df_main for "total_prices" over all dates
    try:
        df_main = df_main.sort_values(['total_price']).reset_index(drop=True)
    except UnboundLocalError:
        df_main = pd.DataFrame()
    return df_main

def save_df_to_json(df, file_path):
    """
    Converts df to json format and saves to file_path

    :param df: df to save as json
    :param file_path: path of saved file

    """
    df_dict = df.to_json(orient='table')
    data = json.loads(df_dict)
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)

def print_top_flights(params, df_common_dest):
    """
    Prints flight info for top N cheapest flights

    :param params: dictionary of user defined params, including number of flights to return
    :param df_common_dest: dataframe of all possible flight combinations, 
    sorted according to total price

    """
    if not df_common_dest.empty :
        for flight in range(int(params['num_flights'])):
            origin_name_1 = df_common_dest.loc[flight, 'origin_city_name_1']
            origin_id_1 = df_common_dest.loc[flight,'origin_iata_id_1']
            carrier_1 = df_common_dest.loc[flight,'carrier_1']
            price_1 = df_common_dest.loc[flight,'price_1']
            date_1 = df_common_dest.loc[flight,'date_1']
            origin_name_2 = df_common_dest.loc[flight,'origin_city_name_2']
            origin_id_2 = df_common_dest.loc[flight,'origin_iata_id_2']
            carrier_2 = df_common_dest.loc[flight,'carrier_2']
            price_2 = df_common_dest.loc[flight,'price_2']
            date_2 = df_common_dest.loc[flight,'date_2']
            dest_name = df_common_dest.loc[flight,'dest_city_name_1']
            dest_id = df_common_dest.loc[flight,'dest_iata_id_1']
            total_price = df_common_dest.loc[flight,'total_price']
            currency = params['currency']

           # print('#' +str(flight+1)+' cheapest flight:')
           # print(f'Date: {date_1}')
           # print(f'First Outbound Journey: {origin_name_1}({origin_id_1}) -> {dest_name}({dest_id})')
           # print(f'with {carrier_1} at {price_1} {currency}')
           # print(f'Second Outbound Journey: {origin_name_2}({origin_id_2}) -> {dest_name}({dest_id})')
           # print(f'Date: {date_2}')
           # print(f'with {carrier_2} at {price_2} {currency}')
           # print(f'For a total price of {total_price} {currency}')
           # print("-----------")
    else:
        print("No common destination found")

def main():
    # get all possible flights and user params from get_data script 
    params, df_outbound, df_inbound = get_data.main()
    # print()

    # get common destinations for outbound and inbound trips
    # print('OUTBOUND FLIGHTS-------')
    # print('Date: ', params['date_outbound'])
    # print('Getting common destinations and calculating prices...')
    df_common_dest_outbound = get_common_dest(df_outbound)
    # print()
    # print('Saving flights to sorted_common_dest.txt')
    save_df_to_json(df_common_dest_outbound, 'Data/sorted_common_dest.json')
    # print()
    # print_top_flights(params, df_common_dest_outbound)

    # if params['date_inbound'] != None:
    # print()
    # print('INBOUND FLIGHTS-------')
    # print('Date: ', params['date_inbound'])
    # print('Getting common destinations and calculating prices...')
    #df_common_dest_inbound = get_common_dest(df_inbound)
    
    # have to figure out how to combine inbound and outbound
    # 

    print()
    print('Done!')


if __name__== "__main__":
    main()