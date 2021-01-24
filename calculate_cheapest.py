import get_data
import pandas as pd
import json

#TODO: extend beyond 2 cities
#      return flight
#      doc

def get_common_dest(df_outbound, df_inbound):
    origin_cities = df_outbound['origin_city_name'].unique()

    # create dataframe to hold all flight combinations with common destination city
    columns = ['common_dest_id', 'common_dest_name', 'total_price']
    for i in range(len(origin_cities)):
        columns.append('origin_id_'+str(i+1))
        columns.append('origin_name_'+str(i+1))
        columns.append('carrier_'+str(i+1))
        columns.append('price_'+str(i+1))     
    df_common_dest = pd.DataFrame(columns = columns)

    # list of flights by origin
    df_origin_list = []

    for city in origin_cities:
        # possible flights per origin
        df_outbound_byOrigin = (df_outbound[ df_outbound['origin_city_name'] == city ])
        df_origin_list.append(df_outbound_byOrigin)

    # assuming 2 origin cities
    for row1 in df_origin_list[0].iterrows():
        for row2 in df_origin_list[1].iterrows():
            if row1[1][7] == row2[1][7]:
                price_1 = row1[1][4]
                price_2 = row2[1][4]
                
                df_common_dest = df_common_dest.append({'common_dest_id': row1[1][3],
                                                        'common_dest_name': row1[1][7],
                                                        'total_price': price_1+price_2,
                                                        'origin_id_1': row1[1][1],
                                                        'origin_name_1': row1[1][6],
                                                        'carrier_1': row1[1][5],
                                                        'price_1': price_1,
                                                        'origin_id_2': row2[1][1],
                                                        'origin_name_2': row2[1][6],
                                                        'carrier_2': row2[1][5],
                                                        'price_2': price_2
                                                    }, ignore_index=True)

    # sort by total price (least to most)
    print('Sorting by price...')
    df_common_dest = df_common_dest.sort_values(['total_price']).reset_index(drop=True)

    if df_inbound.empty == False:
        # same for return flight
        pass

    return df_common_dest

def save_df_to_json(df):
    df_dict = df.to_json(orient='index')
    data = json.loads(df_dict)
    with open('Data/sorted_common_dest', 'w') as outfile:
        json.dump(data, outfile)

def print_top_flights(params, df_common_dest):
    for flight in range(int(params['num_flights'])):
        origin_name_1 = df_common_dest.iloc[flight, 4]
        origin_id_1 = df_common_dest.iloc[flight,3]
        carrier_1 = df_common_dest.iloc[flight,5]
        price_1 = df_common_dest.iloc[flight,6]
        origin_name_2 = df_common_dest.iloc[flight,8]
        origin_id_2 = df_common_dest.iloc[flight,7]
        carrier_2 = df_common_dest.iloc[flight,9]
        price_2 = df_common_dest.iloc[flight,10]
        dest_name = df_common_dest.iloc[flight,1]
        dest_id = df_common_dest.iloc[flight,0]
        total_price = df_common_dest.iloc[flight,2]
        currency = params['currency']

        print(str(flight+1)+'st cheapest flight:')
        print(f'First Outbound Journey: {origin_name_1}({origin_id_1}) -> {dest_name}({dest_id})')
        print(f'with {carrier_1} at {price_1} {currency}')
        print(f'Second Outbound Journey: {origin_name_2}({origin_id_2}) -> {dest_name}({dest_id})')
        print(f'with {carrier_2} at {price_2} {currency}')
        print(f'For a total price of {total_price}')
        print("-----------")

def main():
    # get all possible flights and user params from get_data script 
    params, df_outbound, df_inbound = get_data.main()
    print()
    print('Getting common destinations and calculating prices...')
    df_common_dest = get_common_dest(df_outbound, df_inbound)

    print()
    print('Saving flights to sorted_common_dest.txt')
    save_df_to_json(df_common_dest)

    print()
    print_top_flights(params, df_common_dest)

    print()
    print('Done!')


if __name__== "__main__":
    main()