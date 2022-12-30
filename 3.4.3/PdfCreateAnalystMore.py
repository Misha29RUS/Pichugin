import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdfkit
from statistics import mean
from jinja2 import Environment, FileSystemLoader


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
        self.dataframe['salary'] = self.dataframe[
            ['salary_from', 'salary_to', 'salary_currency', 'published_at']].apply(self.convert_salary, axis=1)
        self.dataframe.drop(labels=['salary_to', 'salary_from', 'salary_currency'], axis=1, inplace=True)
        self.dataframe = self.dataframe.loc[self.dataframe['salary'] != 'nan']
        self.dataframe.to_csv(f'cvs_data.csv', index=False)
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
            multiplier = \
            self.currency_dataframe[self.currency_dataframe['date'] == str(row[3])[:7]][salary_in_foreign_currency].iat[
                0]
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
            data[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]].to_csv(
                f"csv_data\\part_{x}.csv", index=False)


class Report:
    """ Класс для создания графиков в формате .png и отчета в формате .pdf по аналитике вакансий
    """

    def __init__(self, vacancy, area_name, area_dicts, year_dicts):
        """ Инициализирует класс Report

         Args:
            vacancy (str): Название профессии
            area_name (str): Название города
            area_dicts (list[dict]): Список городов
            year_dicts (list[dict]): Список годов
        """
        self.image_create(vacancy, area_name, area_dicts, year_dicts)
        self.pdf_create(vacancy, area_name, area_dicts, year_dicts)

    @staticmethod
    def pdf_create(vacancy, area_name, area_dicts, year_dicts):
        """ Метод для созданию отчета по аналитике вакансий в фомате .pdf

        Args:
            vacancy (str): Название профессии
            area_name (str): Название города
            area_dicts (list[dict]): Список городов
            year_dicts (list[dict]): Список годов
        """
        environment = Environment(loader=FileSystemLoader('.'))
        sample = environment.get_template("pdf_template.html")
        pdf_template = sample.render({'name': vacancy,'area_name': area_name,'area_dict': area_dicts,'year_dict': year_dicts,'keys_0_area': list(area_dicts[0].keys()),
                                      'values_0_area': list(area_dicts[0].values()),'keys_1_area': list(area_dicts[1].keys()),
                                      'values_1_area': list(area_dicts[1].values()),'graph': 'graph.png'})
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        options = {"enable-local-file-access": ""}
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options=options)

    @staticmethod
    def image_create(vacancy, area_name, area_dicts, year_dicts):
        """ Метод для созданию графиков с аналитикой по годам в фомате .png

        Args:
           vacancy (str): Название профессии
            area_name (str): Название города
            area_dicts (list[dict]): Список городов
            year_dicts (list[dict]): Список годов
        """
        graph = plt.figure()
        graph1 = graph.add_subplot(221)
        graph1.set_title("Уровень зарплат по годам")
        graph1.bar(np.arange(len(year_dicts[0].keys())), year_dicts[0].values(), 0.4,
                        label=f"з/п {vacancy.lower()} {area_name.lower()}")
        graph1.set_xticks(np.arange(len(year_dicts[0].keys())), year_dicts[0].keys(), rotation="vertical")
        graph1.tick_params(axis="both", labelsize=8)
        graph1.legend(fontsize=8)
        graph1.grid(True, axis="y")
        graph2 = graph.add_subplot(222)
        graph2.set_title("Количество вакансий по годам")
        graph2.bar(np.arange(len(year_dicts[0].keys())), year_dicts[1].values(), 0.4,
                         label="Количество вакансий \n" + vacancy.lower() + area_name.lower())
        graph2.set_xticks(np.arange(len(year_dicts[0].keys())), year_dicts[1].keys(), rotation="vertical")
        graph2.tick_params(axis="both", labelsize=8)
        graph2.legend(fontsize=8)
        graph2.grid(True, axis="y")
        graph3 = graph.add_subplot(223)
        graph3.set_title("Уровень зарплат по городам")
        graph3.barh(np.arange(len(area_dicts[0].keys())), area_dicts[0].values(), 0.8, align="center")
        graph3.set_yticks(np.arange(len(area_dicts[0].keys())), labels=[key.replace('-', '-\n').replace(' ', '\n') for key in area_dicts[0].keys()],
                          horizontalalignment="right", verticalalignment="center")
        graph3.tick_params(axis="x", labelsize=8)
        graph3.tick_params(axis="y", labelsize=6)
        graph3.invert_yaxis()
        graph3.grid(True, axis="x")
        graph4 = graph.add_subplot(224)
        graph4.set_title("Доля вакансий по городам")
        area_dicts[1] = {'Другие': 1 - sum(area_dicts[1].values()), **area_dicts[1]}
        graph4.pie(area_dicts[1].values(), labels=area_dicts[1].keys(), textprops={'fontsize': 6})
        graph4.axis('equal')
        plt.tight_layout()
        plt.savefig("graph.png")


def dict_sort(current_dict):
    """ Метод для сортировки словаря
    Args:
        current_dict (dict): Исходный словарь
    Returns:
        (dict): Возвращает отсортированный словарь
    """
    return {x: current_dict[x] for x in sorted(current_dict)}


def sort_dict_area(unsorted_dict):
    """ Метод для сортировки по городам
    Args:
        unsorted_dict (dict): Исходный словарь
     Returns:
         Возвращает отсортированный словарь
    """
    return {key: value for key, value in sorted(unsorted_dict.items(), key=lambda item: item[1], reverse=True)[:10]}


if __name__ == '__main__':
    file = input('Введите название файла: ')
    vac_name = input('Введите название профессии: ')
    area_name = input('Введите название региона: ')
    dataframe = pd.read_csv(file)
    exchange_rate = pd.read_csv('exchange_rate_currency.csv')

    dataframe["years"] = dataframe["published_at"].apply(lambda date: int(".".join(date[:4].split("-"))))
    years_list = list(dataframe["years"].unique())
    area_salary, area_vacancy, vacancy_of_profession_salary, vacancy_of_profession_count = {}, {}, {}, {}
    dataframe = DataSetConverter(dataframe, exchange_rate).data_set_converter_create_csv()
    vac_count = len(dataframe)
    dataframe["count"] = dataframe.groupby("area_name")['area_name'].transform("count")
    df_splitted = dataframe[dataframe['count'] >= vac_count * 0.01]
    for city in list(df_splitted["area_name"].unique()):
        salaries = df_splitted[df_splitted['area_name'] == city]
        area_salary[city] = int(salaries['salary'].mean())
        area_vacancy[city] = round(len(salaries) / len(dataframe), 4)

    vacancies = dataframe[dataframe["name"].str.contains(vac_name)]
    for year in years_list:
        vacancy_salary = vacancies[(vacancies['years'] == year) & (vacancies['area_name'] == area_name)]
        if not vacancy_salary.empty:
            vacancy_of_profession_salary[year] = int(vacancy_salary['salary'].mean())
            vacancy_of_profession_count[year] = len(vacancy_salary)

    print("Уровень зарплат по городам (в порядке убывания):", sort_dict_area(area_salary))
    print("Доля вакансий по городам (в порядке убывания):", sort_dict_area(area_vacancy))
    print("Динамика уровня зарплат по годам для выбранной профессии и региона:", dict_sort(vacancy_of_profession_salary))
    print("Динамика количества вакансий по годам для выбранной профессии и региона:", dict_sort(vacancy_of_profession_count))

    dict_of_areas = [sort_dict_area(area_salary), sort_dict_area(area_vacancy)]
    dict_of_years = [dict_sort(vacancy_of_profession_salary), dict_sort(vacancy_of_profession_count)]
    report = Report(vac_name, area_name, dict_of_areas, dict_of_years)