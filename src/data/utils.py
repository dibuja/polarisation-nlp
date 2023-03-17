'''
Module with all the functions that are useful throughout the entire processing 
of data.

1. string_to_list: when saving pandas dataframes as .csv files that contain a 
list within cells, the lists turn into strings. This function fixes that 
turning them back to lists.

'''

import pandas as pd

def string_to_list(string: str):

    lst = []
    string = string.strip('][').split(', ')
    for item in string:
        lst.append(item.replace("'", ""))

    return lst