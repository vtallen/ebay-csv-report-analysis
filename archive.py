# All of the functions that I made but need to rework back into the main program    
'''
Parameters:
    data_frame: pandas data frame

Returns:
    A dictionary in the following format, containing all states + cities,
    as well as how many orders were sent to each city

    {
        "NY":{
            "TOTAL":15
            "Brooklyn":10
            "New York":5
        }
    }
'''
def get_location_stats(data_frame):
    location_dict = {} 

    for index, row in data_frame.iterrows():
        state = row['Buyer State']
        city = row['Buyer City']

        if state in location_dict:
            location_dict[state]["TOTAL"] += 1

            if city in location_dict[state]:
                location_dict[state][city] += 1 
            else:
                location_dict[state][city] = 1

        else:
            location_dict[state] = {
                    "TOTAL":1,
                    city:1
                    }

    return location_dict


def get_top_state(location_stats_dict):
    top_state = ''
    top_state_count = 0

    for key in location_stats_dict.keys():
        if location_stats_dict[key]["TOTAL"] > top_state_count:
            top_state = key
            top_state_count = location_stats_dict[key]["TOTAL"]
    
    return top_state

def get_top_city(location_stats_dict):
    top_city = ''
    top_city_state = ''
    top_city_count = 0

    for state in location_stats_dict.keys():
        for city in location_stats_dict[state].keys():
            if city == "TOTAL":
                continue
            
            if location_stats_dict[state][city] > top_city_count:
                top_city = city
                top_city_state = state
                top_city_count = location_stats_dict[state][city]
    
    return [top_city_state, top_city]

