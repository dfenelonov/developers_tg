from lxml import html
from random import shuffle
from urllib.parse import quote, quote_plus, unquote_plus
import re
import gzip
from time import sleep
import numpy as np
import pandas as pd
import requests
import datetime as dt

import os


class GoogleParser:
    @staticmethod
    def get_inn(I_ORG, I_LOC='', I_PER=''):
        """
        Сбор инн по названию и локации из google
        """
        sleep(3)

        inns, query_results = [], []
        inn_re = re.compile(r'(ИНН|инн).?(\d{9,12})')

        # т.к. буквы русские используем quote_plus для кодирования не ASCII символов
        try:
            url = 'https://www.google.com/search?q={}'.format(
                quote_plus((I_ORG + ' инн ' + I_LOC + ' ' + I_PER).strip()))
            response = requests.get(url)
        except Exception as err:
            try:
                sleep(10)
                url = 'https://www.google.com/search?q={}'.format(
                    quote_plus((I_ORG + ' инн ' + I_LOC + ' ' + I_PER).strip()))
                response = requests.get(url, verify=False)  #### добавлен verify=False
            except Exception as err:
                print(err)

        if response.status_code == 429:
            sleep(500)
            return

        if response.status_code == 443:
            print('443: max retries')
            sleep(100)
            return

        if response.status_code == 404:
            print('404: not found')
            return

        if response.status_code != 200:
            print('Response status:', response.status_code)
            sleep(200)
            return

        tree = html.fromstring(response.text)
        # достаем поисковые выдачи
        query_results = tree.xpath('//*[@id="main"]/div')

        if len(query_results) > 0:
            for q in query_results[:10]:
                if q.xpath('descendant::*/text()') != None:
                    search = inn_re.search(' '.join(q.xpath('descendant::*/text()')))
                    if search != None:
                        inn = search.group(2)
                        try:
                            if GoogleParser.check_inn(inn):
                                inns.append(inn)
                        except Exception as ex:
                            print(ex)

        res = GoogleParser.most_common(inns)
        return res

    @staticmethod
    def most_common(lst):
        if len(lst) == 0:
            return None
        elif len(set(lst)) != len(lst):
            return max(set(lst), key=lst.count)
        else:
            return lst[0]

    @staticmethod
    def check_inn(inn):
        """
        Проверка чек-суммы ИНН (штука Габдулханова Марселя)
        """
        ip2 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        ip1 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        ul = [2, 4, 10, 3, 5, 9, 4, 6, 8]

        if len(inn) == 9 or len(inn) == 11:
            inn = '0' + inn
        elif len(inn) < 9 or len(inn) > 12:
            return False

        if len(inn) == 12:
            chck_sum = 0
            for i, n in enumerate(inn[:10]):
                chck_sum += int(n) * ip2[i]
            if str(chck_sum % 11)[-1] != inn[10]:
                return False
            chck_sum = 0
            for i, n in enumerate(inn[:11]):
                chck_sum += int(n) * ip1[i]
            if str(chck_sum % 11)[-1] != inn[11]:
                return False
            return True

        if len(inn) == 10:
            chck_sum = 0
            for i, n in enumerate(inn[:9]):
                chck_sum += int(n) * ul[i]
            if str(chck_sum % 11)[-1] != inn[9]:
                return False
            return True

    @staticmethod
    def third_function(I_ORG):
        inn = GoogleParser.get_inn(I_ORG, I_LOC='', I_PER='')
        if inn is not None and GoogleParser.check_inn(inn):
            return inn
        # return GoogleParser.check_inn(inn)
        else:
            return 'Nan'