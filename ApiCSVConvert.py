import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from xml.etree import ElementTree
import requests
from statistics import mean


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
        Returns:
            DataFrame: Возвращает фрагмент с курсами валют в разные годы
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
        return currency_dataframe


class DataSetConverter:
    """ Класс для конвертации валют и создания соответствующего файла в формате .cvs

    Attributes:
        dataframe (DataFrame): Первоночальный  фрейм c данными о вакансиях
        currency_dataframe (DataFrame): Фрейм с данными о курсах валют на даты, указанные в вакансиях
        exchange_rates (list[str]): Допуступные для конвертации валюты
    """
    def __init__(self, dataframe, currency_dataframe):
        """ Инициализирует класс DataSetConverter

        Args:
            dataframe (DataFrame): Первоночальный  фрейм c данными о вакансиях после создания файла с курсами валют
            currency_dataframe (DataFrame): Фрейм с данными о курсах валют на даты, указанные в вакансиях
        """
        self.dataframe = dataframe
        self.currency_dataframe = currency_dataframe
        self.exchange_rates = list(self.currency_dataframe.keys()[2:])

    def data_set_converter_create_csv(self):
        """ Метод для создания файла в формате .csv, содержащим данные с обработанными вакансиями,
        у которых зарплата переведена по курсу валют

        """
        self.dataframe.insert(1, 'salary', None)
        self.dataframe['salary'] = self.dataframe[['salary_from', 'salary_to', 'salary_currency', 'published_at']].apply(self.convert_salary, axis=1)
        self.dataframe.drop(labels=['salary_to', 'salary_from', 'salary_currency'], axis=1, inplace=True)
        self.dataframe = self.dataframe.loc[self.dataframe['salary'] != 'nan']
        self.dataframe.to_csv('exchange_rate_currency_convert.csv', index=False)

    def convert_salary(self, row):
        """ Метод для получения значения зарплаты по вакансии, переведенной в рубли по курсу валют.
        Если значения недопустимы, функция отсанавливается и возвращает 'nan'.

        Args:
            row (pd.Series): Строка рассматриваемой вакансии из DataFrame

        Returns:
            str or float: Возвращает значение зарплаты или 'nan',если значения недопустимы
        """
        salary_in_foreign_currency = str(row[2])
        list_of_salary = list(filter(lambda x: str(x) != 'nan', row[:2]))
        if salary_in_foreign_currency == 'nan':
            return 'nan'

        if len(list_of_salary) != 0:
            convert_salary = mean(list_of_salary)
        else:
            return 'nan'

        if salary_in_foreign_currency != 'RUR' and salary_in_foreign_currency in self.exchange_rates:
            multiplier = self.currency_dataframe[self.currency_dataframe['date'] == str(row[3])[:7]][salary_in_foreign_currency].iat[0]
            convert_salary *= multiplier
        return convert_salary


data_set = DataSet('vacancies_dif_currencies.csv')
data_set_currency = DataSetCurrency(data_set.dataframe_sort)
data_set_currency_csv = data_set_currency.get_currency_in_csv(list(data_set.dict_of_amount.keys()), data_set.older_date, data_set.newest_date)
DataSetConverter(data_set.dataframe_sort, data_set_currency_csv).data_set_converter_create_csv()
