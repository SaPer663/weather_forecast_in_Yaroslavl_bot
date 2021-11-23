import json
import os
import tempfile

from collections import OrderedDict
from datetime import datetime as dt, timedelta as td
from typing import List, Optional

import requests

from bs4 import BeautifulSoup
from bs4.element import NavigableString, ResultSet, Tag

SLUG = 'weather-yaroslavl-4313'
N_TAGIL = 'weather-nizhny-tagil-4478'


class WeatherForecastParser:
    """Парсит прогноз погоды с сайта gismetio.ru
    В конструктор класса необходимо передать slug населённого пунктаю
    """

    TAG_DIV = 'div'
    CLASS_TOOL_TIP = 'tooltip'
    CLASS_CELL = 'cell'
    CLASS_HOVER = 'hover'

    def __init__(self, slug: str) -> None:
        self.slug: str = slug
        self._soup: BeautifulSoup = BeautifulSoup(self._response_text(),
                                                  'lxml')
        self._get_cleaned_data: ResultSet = self._get_html_by_class_div(
            [self.CLASS_TOOL_TIP, self.CLASS_CELL])

    def _response_text(self) -> str:
        """Возвращает строку html разметки страницы полученной по url."""
        url = f'https://www.gismeteo.ru/{self.slug}/month/'
        return requests.get(
            url,
            headers={
                'user-agent': ('Mozilla/5.0 (X11; Linux x86_64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/84.0.4147.89 Safari/537.36')}
        ).text

    def _get_bs4_elements_tag(
            self, raw_data: BeautifulSoup, name_tag: str, class_tag: str
    ) -> ResultSet:
        """Возвращает объект типа ResultSet - список объектов html разметки с
         заданным тегом и классом тега.
        Принимает объект типа BeautifulSoup с содержанием html разметки,
        name_tag - тег, типа str, класс тега типа str.
        """
        return raw_data.findAll(name_tag, class_=class_tag)

    def _get_one_bs4_element_tag(
            self, raw_data: BeautifulSoup, name_tag: str, class_tag: str
    ) -> Tag:
        """Возвращает объект типа bs4.element.Tag - объект html разметки с
        заданным тегом и тегом класса.
         """
        return raw_data.find(name_tag, class_=class_tag)

    def _get_html_by_class_div(self, class_list: List[str]) -> ResultSet:
        """Возвращает ResultSet для div с данными класамми.
        Принимает список классов тега div.
        """
        classses = ' '.join(class_list)
        return self._get_bs4_elements_tag(self._soup, self.TAG_DIV, classses)

    def _parse_date(self, bs4_element_tag: Tag) -> NavigableString:
        """Возвращает объект NavigableString - строка содержимого тега с датой.
        Принимает объект типа bs4.element.Tag.
        """
        result = self._get_one_bs4_element_tag(bs4_element_tag, 'div', 'date')
        if len(result.contents) > 1:
            return result.contents[0].contents[0].string
        else:
            return result.contents[0].string

    def _parse_temp_max(self, bs4_element_tag: Tag) -> NavigableString:
        """Возвращает объект NavigableString - строка содержимого тега с
        максимальной температурой воздуха за один день.
        Принимает объект типа bs4.element.Tag.
        """
        result = self._get_one_bs4_element_tag(
            bs4_element_tag, 'div', 'temp_max')
        return self._get_one_bs4_element_tag(
            result, 'span', 'unit_temperature_c').string

    def _parse_temp_min(self, bs4_element_tag: Tag) -> NavigableString:
        """Возвращает объект NavigableString - строка содержимого тега с
        минимальной температурой воздуха за один день.
        Принимает объект типа bs4.element.Tag.
        """
        result = self._get_one_bs4_element_tag(
            bs4_element_tag, 'div', 'temp_min')
        return self._get_one_bs4_element_tag(
            result, 'span', 'unit_temperature_c').string

    def _dictionary_of_dates(self) -> OrderedDict[dt, NavigableString]:
        current_date = dt.now()
        step = td(days=1)
        dictionary: OrderedDict = OrderedDict()
        count = 0
        while count < 20:
            dictionary[current_date.strftime('%d.%m')] = {}
            current_date += step
            count += 1
        return dictionary

    def get_filled_dictionary(self) -> OrderedDict[dt, NavigableString]:
        list_data = list(self._get_cleaned_data)
        data_dictionary = self._dictionary_of_dates()
        for data, elem in zip(list_data, data_dictionary.keys()):
            data_dictionary[elem]['temp_max'] = (self._parse_temp_max(data)
                                                 .strip())
            data_dictionary[elem]['temp_min'] = (self._parse_temp_min(data)
                                                 .strip())
            data_dictionary[elem]['date'] = (self._parse_date(data)
                                             .strip().split()[0])
            data_dictionary[elem]['data-text'] = data['data-text']
        return data_dictionary


class JsonStorage:
    """Реализует хранение данных в json файле."""

    def __init__(self, path: Optional[str] = None) -> None:
        if path is None:
            self.path: str = os.path.join(tempfile.gettempdir(),
                                          'storage.json')
        self

    def write(self, data_dict: dict):
        """Метод производит запись в файл.
        Принемает словарь с данными.
        """
        with open(self.path, "w") as write_file:
            json.dump(data_dict, write_file)

    def read(self):
        with open(self.path) as file:
            return json.load(file)
