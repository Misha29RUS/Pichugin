import pandas as pd
import sqlite3
from statistics import mean

class DataSetConverter:
    """ Класс для конвертации валют и создания соответствующего файла в формате .cvs

    Attributes:
        dataframe (DataFrame): Первоночальный  фрейм c данными о вакансиях
        currency_data_base (Connection): Подключенная базы данных с информацией о курсах валют
        currencies (List[str]): Допустимые валюты
    """
    def __init__(self, dataframe):
        """ Инициализирует класс DataSetConverter

        Attributes:
            dataframe (DataFrame): Первоночальный  фрейм c данными о вакансиях после создания файла с курсами валют
        """
        self.dataframe = dataframe
        self.currency_data_base = sqlite3.connect('data_base_3.5.1.sqlite')
        self.currencies = list(pd.read_sql("select * from 'data_base_3.5.1.sqlite'", self.currency_data_base).keys()[1:])


    def data_set_converter_create_csv(self):
        """ Метод для создания файла в формате .csv, содержащим данные с обработанными вакансиями,
        у которых зарплата переведена по курсу валют
        """
        self.dataframe.insert(1, 'salary', None)
        self.dataframe['salary'] = self.dataframe[['salary_from', 'salary_to', 'salary_currency', 'published_at']].apply(self.convert_salary, axis=1)
        self.dataframe.drop(labels=['salary_to', 'salary_from', 'salary_currency'], axis=1, inplace=True)
        self.dataframe = self.dataframe.loc[self.dataframe['salary'] != 'nan']
        self.dataframe.to_csv('csv_result.csv', index=False)


    def convert_salary(self, row):
        """ Метод для получения значения зарплаты по вакансии, переведенной в рубли по курсу валют.
        Если значения недопустимы, функция отсанавливается и возвращает 'nan'.

        Attributes:
            row (pd.Series): Строка рассматриваемой вакансии из DataFrame
        Returns:
            str or float: Возвращает значение зарплаты или 'nan',если значения недопустимы
        """
        salary_currency = str(row[2])
        salary_list = list(filter(lambda x: str(x) != 'nan', row[:2]))
        if salary_currency == 'nan':
            return 'nan'

        if len(salary_list) != 0:
            salary = mean(salary_list)
        else:
            return 'nan'

        if salary_currency != 'RUR' and salary_currency in self.currencies:
            multiplier = pd.read_sql(f"select {salary_currency} from 'data_base_3.5.1.sqlite' where date='{str(row[3])[:7]}'", self.currency_data_base)[f'{salary_currency}'][0]
            if multiplier is not None:
                salary *= multiplier
            else:
                return 'nan'
        return salary

    def csv_to_vacancy_sql(self, name_of_data_base):
        """ Метод конвертации файла в формате .csv в базу данный в формате .sqlite

        Attributes:
            name_of_data_base (str): Имя базы данных
        """
        self.data_set_converter_create_csv()
        connect = sqlite3.connect(name_of_data_base)
        self.dataframe.to_sql(name=name_of_data_base, con=connect, if_exists='replace', index=False)
        connect.commit()


DataSetConverter(pd.read_csv('vacancies_dif_currencies.csv')).csv_to_vacancy_sql('data_base_3.5.2.sqlite')