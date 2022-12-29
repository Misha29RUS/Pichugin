import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from xml.etree import ElementTree
import requests


class DataSet:
    """ Класс для объектов, хранящих в себе данные о вакансиях

    Attributes:
        dataframe (DataFrame): Фрейм с данными о вакансиях
        dataframe_sort (DataFrame): Отсорированный фрейм с данными о вакансиях
        dict_of_amount (dict): Словарь с количеством встечающихся валют в вакансиях
        older_date (date): Самая старая вакансия в списке
        newest_date (date): Самая новая вакансия в списке
    """
    def __init__(self, file_name):
        """ Инициализирует класс DataSet

        Args:
            file_name (str): Имя файла c исходными данными в формате .csv
        """
        self.dataframe = pd.read_csv(file_name)
        self.dataframe_sort = self.dataframe.sort_values(by='published_at').reset_index(drop=True)
        self.dict_of_amount = {}
        self.get_count_amount()
        self.older_date = self.get_date_in_format(range(len(self.dataframe_sort)))
        self.newest_date = self.get_date_in_format(range(len(self.dataframe_sort) - 1, -1, -1))

    def get_count_amount(self):
        """ Метод подсчёта колличества встречающихся валют в вакансиях

        """
        for x in range(len(self.dataframe_sort)):
            key = self.dataframe_sort['salary_currency'][x]
            if str(key) == 'nan' or str(key) == 'RUR':
                continue
            if key not in self.dict_of_amount:
                self.dict_of_amount[key] = 0
            self.dict_of_amount[key] += 1
        print(self.dict_of_amount)
        self.dict_of_amount = dict([x for x in self.dict_of_amount.items() if x[1] > 5000])
        self.dict_of_amount = dict(sorted(self.dict_of_amount.items(), key=lambda x: x[0]))

    def get_date_in_format(self, date_interval):
        """ Метод перебора списка вакансий для поиска самой старой и новой.
        Args:
            date_interval: Показывает промежуток вакансий, который нужно рассмотреть

        Returns:
            datetime.date: Возвращает дату вакансии в заданном формате
        """
        for x in date_interval:
            if self.dataframe_sort['salary_currency'][x] in self.dict_of_amount:
                return datetime.strptime(self.dataframe_sort['published_at'][x], '%Y-%m-%dT%H:%M:%S%z').date()


class DataSetCurrency:
    """ Класс для данных о курсах валют

    Attributes:
        dataframe (DataFrame): Фрейм с данными о вакансиях
    """
    def __init__(self, dataframe):
        """ Инициализирует класс CurrencyData
        Args:
            dataframe (DataFrame): Фрейм с данными о вакансиях из класса DataSet
        """
        self.dataframe = dataframe

    @staticmethod
    def get_year_interval(start_date, end_date):
        """ Метод для определения нужных дат в форме месяца и года соответственно для использования в запросах
        Args:
            start_date (datetime.date): Начальная дата
            end_date (datetime.date): Конечная дата
        Returns:
            list: Возвращает список дат
        """
        result_date_list = []
        start_date = start_date + relativedelta(day=1)
        end_date = end_date + relativedelta(day=28)
        while start_date < end_date:
            result_date_list.append(start_date.strftime('%m/%Y'))
            start_date = start_date + relativedelta(months=1)
        return result_date_list

    def get_currency_in_csv(self, currency_list, start_date, end_date):
        """ Метод формирования файла с курсами валют в зависимости от даты в формате .csv
        Args:
            currency_list (list): Список рассматриваемых валют
            start_date (datetime.date): Начальная дата
            end_date (datetime.date): Конечная дата
        """
        currency_dataframe = pd.DataFrame(columns=['date'] + currency_list)
        dates_list = self.get_year_interval(start_date, end_date)
        for date in dates_list:
            answer = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{date}d=1')
            answer = ElementTree.fromstring(answer.content.decode("WINDOWS-1251"))
            currency_dict = {x: '' for x in currency_list}
            for x in answer.findall('./Valute'):
                if x.find('./CharCode').text in currency_list:
                    currency_dict[x.find('./CharCode').text] = \
                        round(float(x.find('./Value').text.replace(',', '.')) /
                              int(x.find('./Nominal').text), 4)
                    if all(currency_dict.values()):
                        break
            currency_dict = sorted(currency_dict.items(), key=lambda x: x[0])
            current_course = [x[1] for x in currency_dict]
            currency_dataframe.loc[len(currency_dataframe.index)] = [datetime.strptime(date, '%m/%Y').strftime('%Y-%m')] \
                                                                    + current_course
        currency_dataframe.to_csv('exchange_rate_currency.csv', index=False)


data_set = DataSet('vacancies_dif_currencies.csv')
data_set_currency = DataSetCurrency(data_set.dataframe_sort)
data_set_currency.get_currency_in_csv(list(data_set.dict_of_amount.keys()), data_set.older_date, data_set.newest_date)
