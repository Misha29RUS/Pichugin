import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdfkit
from statistics import mean
from jinja2 import Environment, FileSystemLoader
from concurrent import futures


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

    def data_set_converter_create_csv(self, date):
        """ Метод для создания файла в формате .csv, содержащим данные с обработанными вакансиями,
        у которых зарплата переведена по курсу валют

        """
        self.dataframe.insert(1, 'salary', None)
        self.dataframe['salary'] = self.dataframe[['salary_from', 'salary_to', 'salary_currency', 'published_at']].apply(self.convert_salary, axis=1)
        self.dataframe.drop(labels=['salary_to', 'salary_from', 'salary_currency'], axis=1, inplace=True)
        self.dataframe = self.dataframe.loc[self.dataframe['salary'] != 'nan']
        self.dataframe.to_csv(f'csv_data\\part_{date}.csv', index=False)
        return self.dataframe

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
            convert_salary = multiplier * convert_salary
        return convert_salary


class SplittingCSV:
    """ Класс для разделения исходного файла в формате .csv с вакансиями на несколько по годам
    """
    def __init__(self, file_name):
        """ Инициализирует класс SeparateCSV

        Args:
            file_name (str): Имя исходного файла в формате .csv
        """
        self.dataframe = pd.read_csv(file_name)
        self.dataframe["years"] = self.dataframe["published_at"].apply(lambda x: int(".".join(x[:4].split("-"))))
        self.years = list(self.dataframe["years"].unique())

        for x in self.years:
            data = self.dataframe[self.dataframe["years"] == x]
            data[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]].to_csv(f"csv_data\\part_{x}.csv", index=False)

class Report:
    """ Класс для создания графиков в формате .png и отчета в формате .pdf по аналитике вакансий
    """
    def __init__(self, vacancy, dict_of_analytics_by_years):
        """ Инициализирует класс Report

         Args:
            vacancy (str): Название профессии
            dict_of_analytics_by_years (list[dict]): Словари с аналитикой по профессиям, учитывая выбранную и года
        """
        self.image_create(vacancy, dict_of_analytics_by_years)
        self.pdf_create(vacancy, dict_of_analytics_by_years)

    @staticmethod
    def pdf_create(vacancy, dict_of_analytics_by_years):
        """ Метод для созданию отчета по аналитике вакансий в фомате .pdf

        Args:
            vacancy (str): Название профессии
            dict_of_analytics_by_years (list[dict]): Словари с аналитикой по профессиям, учитывая выбранную и года
        """
        environment = Environment(loader=FileSystemLoader('.'))
        sample = environment.get_template("pdf_template.html")
        pdf_template = sample.render({'name': vacancy, 'dicts': dict_of_analytics_by_years, 'graph': 'graph.png'})
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        options = {"enable-local-file-access": ""}
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options=options)

    @staticmethod
    def image_create(vacancy, dict_of_analytics_by_years):
        """ Метод для созданию графиков с аналитикой по годам в фомате .png

        Args:
            vacancy (str): Название профессии
            dict_of_analytics_by_years (list[dict]): Словари с аналитикой по профессиям, учитывая выбранную и года
        """
        graph = plt.figure()
        x_axis = np.arange(len(dict_of_analytics_by_years[0].keys()))
        graph1 = graph.add_subplot(221)
        graph1.set_title("Уровень зарплат по годам")
        graph1.bar(x_axis + 0.4 / 2, dict_of_analytics_by_years[1].values(), 0.4, label="з/п" + vacancy.lower())
        graph1.bar(x_axis - 0.4 / 2, dict_of_analytics_by_years[0].values(), 0.4, label="средняя з/п")
        graph1.set_xticks(x_axis, dict_of_analytics_by_years[0].keys(), rotation="vertical")
        graph1.legend(fontsize=8)
        graph1.tick_params(axis="both", labelsize=8)
        graph1.grid(True, axis="y")
        graph2 = graph.add_subplot(222)
        graph2.set_title("Количество вакансий по годам")
        graph2.bar(x_axis + 0.4 / 2, dict_of_analytics_by_years[3].values(), 0.4, label="Количество вакансий \n" + vacancy.lower())
        graph2.bar(x_axis - 0.4 / 2, dict_of_analytics_by_years[2].values(), 0.4, label="Количество вакансий")
        graph2.set_xticks(x_axis, dict_of_analytics_by_years[2].keys(), rotation="vertical")
        graph2.legend(fontsize=8)
        graph2.tick_params(axis="both", labelsize=8)
        graph2.grid(True, axis="y")
        plt.tight_layout()
        plt.savefig("graph.png")

def dict_sort(current_dict):
    """ Метод для сортировки словаря
    Args:
        current_dict (dict): Исходный словарь
    Returns:
        (dict): Возвращает отсортированный словарь
    """
    # sorted_dict = {}
    # for x in sorted(unsorted_dict):
    #     sorted_dict[x] = unsorted_dict[x]
    return {x: current_dict[x] for x in sorted(current_dict)}


exchange_rate = pd.read_csv('exchange_rate_currency.csv')

def proccess(args):
    """ Метод для обработки данных за год и формирования словаря с аналитикой
    Args:
        args (tuple): Аргументы
    Returns:
        (list[dict]): Возвращает словарь с аналитикой
    """
    year = args[1]
    dataframe = pd.read_csv(f'csv_data\\part_{year}.csv')
    dataframe = DataSetConverter(dataframe, exchange_rate).data_set_converter_create_csv(year)

    vac_df = dataframe[dataframe["name"].str.contains(args[0])]

    year_of_salary = {year: []}
    year_of_vac = {year: 0}
    year_of_profession_salary = {year: []}
    year_of_profession_vacancy = {year: 0}

    year_of_salary[year] = int(dataframe['salary'].mean())
    year_of_vac[year] = len(dataframe)
    year_of_profession_salary[year] = int(vac_df['salary'].mean())
    year_of_profession_vacancy[year] = len(vac_df)

    return [year_of_salary, year_of_vac, year_of_profession_salary, year_of_profession_vacancy]


if __name__ == '__main__':

    file = input('Введите название файла: ')
    vac_name = input('Введите название профессии: ')
    splitted_csv = SplittingCSV(file)
    dataframe = splitted_csv.dataframe

    year_of_salary, year_of_vacancy, year_of_profession_salary, year_of_profession_vacancy = {}, {}, {}, {}

    executor = futures.ProcessPoolExecutor()
    for x in splitted_csv.years:
        answer = executor.submit(proccess, (vac_name, x)).result()
        year_of_salary.update(answer[0])
        year_of_vacancy.update(answer[1])
        year_of_profession_salary.update(answer[2])
        year_of_profession_vacancy.update(answer[3])

    print("Динамика уровня зарплат по годам:", dict_sort(year_of_salary))
    print("Динамика количества вакансий по годам:", dict_sort(year_of_vacancy))
    print("Динамика уровня зарплат по годам для выбранной профессии:", dict_sort(year_of_profession_salary))
    print("Динамика количества вакансий по годам для выбранной профессии:", dict_sort(year_of_profession_vacancy))

    result_analytics_dicts = [dict_sort(year_of_salary), dict_sort(year_of_profession_salary), dict_sort(year_of_vacancy), dict_sort(year_of_profession_vacancy)]
    report = Report(vac_name, result_analytics_dicts)