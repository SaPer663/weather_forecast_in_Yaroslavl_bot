import json
import re
import requests
from bs4 import BeautifulSoup as beautifulsoup
from collections import OrderedDict
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import date



def response_text():
    url = 'https://www.gismeteo.ru/weather-yaroslavl-4313/month/'
    return requests.get(url, headers={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) \
                                      AppleWebKit/537.36 (KHTML, like Gecko)\
                                      Chrome/84.0.4147.89 Safari/537.36'}).text

def get_bs4_elements_tag(search_location, name_tag, class_tag):
    return search_location.findAll(name_tag, class_=class_tag)


soup = beautifulsoup(response_text(), 'lxml')
div_tooltip_cell = get_bs4_elements_tag(soup, 'div', 'tooltip cell')
div_tooltip_cell_hover = get_bs4_elements_tag(soup, 'div', 'tooltip cell _hover')



def get_bs4_element_tag(search_location, name_tag, class_tag):
    return search_location.find(name_tag, class_=class_tag)
    
def parse_date(bs4_element_tag):
    result = get_bs4_element_tag(bs4_element_tag, 'div', 'date')
    if len(result.contents) > 1:
        return result.contents[0].contents[0].string
    else:
        return result.contents[0].string


def parse_temp_max(bs4_element_tag):
    result = get_bs4_element_tag(bs4_element_tag, 'div', 'temp_max')
    return get_bs4_element_tag(result, 'span', 'unit_temperature_c').string

def parse_temp_min(bs4_element_tag):
    result = get_bs4_element_tag(bs4_element_tag, 'div', 'temp_min')
    return get_bs4_element_tag(result, 'span', 'unit_temperature_c').string

def dictionary_of_dates():
    current_date = dt.now()
    step = td(days=1)
    dictionary = OrderedDict()
    count = 0
    while count < 25:
        dictionary[current_date.strftime('%d.%m')] = {}
        current_date += step
        count +=1
    return dictionary

def get_filled_dictionary():
    list_data = list(div_tooltip_cell_hover) + list(div_tooltip_cell)
    data_dictionary = dictionary_of_dates()
    for data, elem in zip(list_data, data_dictionary.keys()):
        dt = parse_date(data)
        mx = parse_temp_max(data)
        mn = parse_temp_min(data)
        data_dictionary[elem]['temp_max'] = mx.strip()
        data_dictionary[elem]['temp_min'] = mn.strip() 
        data_dictionary[elem]['data-text'] = data['data-text']
        data_dictionary[elem]['date'] = dt.strip().split()[0]
    return data_dictionary


def json_file_update():
    with open("data_file.json", "w") as write_file:
        json.dump(get_filled_dictionary(), write_file)

def json_file_read():
    with open("data_file.json") as file:
        return json.load(file)
    