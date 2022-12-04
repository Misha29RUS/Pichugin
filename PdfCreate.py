import csv
from datetime import datetime
from statistics import mean

import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import openpyxl.styles.numbers
import pdfkit
from jinja2 import Environment, FileSystemLoader
from openpyxl.styles import NamedStyle, Border, Side, Font


class SalaryDict:
    """Класс для хранения и предоставления словаря по зарплате

    Attributes:
        salary_dictionary (dict): Словарь зарплат
        __average_salary_dictionary (dict): Словарь средних зарплат
    """
    def __init__(self):
        """Инициализирует объекты SalaryDict

        """
        self.salary_dictionary = {}
        self.__average_salary_dictionary = {}

    def add(self, key, salary):
        """Добавление в словарь по ключу и зарплате

        Args:
            key (str): Ключ
            salary (int): Зарплата

        Returns:
            dict: Возвращает словарь с добавленным значением
        """

        if self.salary_dictionary.get(key) is None:
            self.salary_dictionary[key] = []
        return self.salary_dictionary[key].append(salary)

    def average_salary(self):
        """Метод для формирования словаря средней заработной платы

        Returns:
            dict: Словарь средней заработной платы
        """
        for key, value in self.salary_dictionary.items():
            self.__average_salary_dictionary[key] = int(mean(value))
        return self.__average_salary_dictionary

    def top_salary(self, top_cities):
        """Метод для формирования словаря самых высокооплачеваемых зарплат

        Args:
            top_cities (list): Список городов

        Returns:
            dict: Словарь самых высокооплачеваемых зарплат
        """
        self.average_salary()
        sorted_dictionary = dict(sorted(self.__average_salary_dictionary.items(), key=lambda x: x[1], reverse=True))
        top_salary_dictionary = {}
        for key, value in sorted_dictionary.items():
            if key in top_cities:
                top_salary_dictionary[key] = value
        return {x: top_salary_dictionary[x] for x in list(top_salary_dictionary)[:10]}


class CountDict:
    """Класс для хранения и предоставления словаря по количеству

    Attributes:
        length (int): Длина словаря
        count_dict (dict): Словарь по колличеству
        city_list (list): Список городов
        top_percentage_dict (dict): Словарь топ 10 вакансий по колличеству
    """
    def __init__(self):
        """
        Инициализирует объекты CountDict
        """
        self.length = 0
        self.count_dict = {}
        self.city_list = []
        self.top_percentage_dict = {}

    def add(self, key):
        """ Добавление в словарь по ключу

        Args:
            key (str): Ключ
        """
        if self.count_dict.get(key) is None:
            self.count_dict[key] = 0
        self.count_dict[key] += 1
        self.length += 1

    def percentage(self):
        """Делает выборку по вакансиям от процента длины словаря
        """
        percentage_dict = {}
        for key, value in self.count_dict.items():
            percentage = value / self.length
            if percentage >= 0.01:
                self.city_list.append(key)
                percentage_dict[key] = round(percentage, 4)
        sort_dict = dict(sorted(percentage_dict.items(), key=lambda x: x[1], reverse=True))
        self.top_percentage_dict = {x: sort_dict[x] for x in list(sort_dict)[:10]}


class Vacancy:
    """Класс для операций(форматированию) по вакансиям

    Attributes:
        __dictionary_currency_to_rub (dict): Словарь для конвертации в рубли
        job_name (str): Название профессии
        salary (int): Зарплата вакансии
        area_name (str): Город вакансии
        year(int): Год публикации вакансии
    """

    def __init__(self, fields):
        """Инициализирует объекты Vacancy

        Args:
            fields (dict): Словарь вакансии
        """
        self.__dictionary_currency_to_rub = {
            "AZN": 35.68,
            "BYR": 23.91,
            "EUR": 59.90,
            "GEL": 21.74,
            "KGS": 0.76,
            "KZT": 0.13,
            "RUR": 1,
            "UAH": 1.64,
            "USD": 60.66,
            "UZS": 0.0055,
        }
        self.job_name = fields['name']
        self.salary = int(
            (float(fields['salary_from']) + float(fields['salary_to'])) / 2 * self.__dictionary_currency_to_rub[
                fields['salary_currency']])
        self.area_name = fields['area_name']
        self.year = int(datetime.strptime(fields['published_at'], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y"))


class Total:
    """Класс для представления данных анализа вакансий


    Attributes:
        dynamics_salary_by_year (dict): Словарь оклад:год
        dynamics_count_by_year (dict): Словарь колличества оклад:год
        dynamics_job_salary_year (dict): Словарь работа:год
        dynamics_job_count_year (dict):Словарь колличества оработа:год
        dynamics_job_salary_city (dict): Словарь работа:город
        dynamics_job_count_city (dict):Словарь колличества работа:город

    """
    def __init__(self):
        """Инициализирует объекты Total

        """
        self.dynamics_salary_by_year = SalaryDict()
        self.dynamics_count_by_year = CountDict()
        self.dynamics_job_salary_year = SalaryDict()
        self.dynamics_job_count_year = CountDict()
        self.dynamics_job_salary_city = SalaryDict()
        self.dynamics_job_count_city = CountDict()

    def get_data(self, vacancies, job_name):
        """Анализ данных по вакансиям

        Args:
           vacancies (list): Своварь вакансий
           job_name (str): Название вводимой профессии

        Returns:
            self: Возвращает объект класса Total
        """
        self.job_name = job_name
        for vacancy in vacancies:
            self.dynamics_salary_by_year.add(vacancy.year, vacancy.salary)
            self.dynamics_count_by_year.add(vacancy.year)
            self.dynamics_job_salary_city.add(vacancy.area_name, vacancy.salary)
            self.dynamics_job_count_city.add(vacancy.area_name)
            if job_name in vacancy.job_name:
                self.dynamics_job_salary_year.add(vacancy.year, vacancy.salary)
                self.dynamics_job_count_year.add(vacancy.year)
        if self.dynamics_job_salary_year.salary_dictionary == {}:
            self.dynamics_job_salary_year.salary_dictionary = {i: [0] for i in
                                                               self.dynamics_salary_by_year.salary_dictionary.keys()}
        if self.dynamics_job_count_year.count_dict == {}:
            self.dynamics_job_count_year.count_dict = {i: 0 for i in self.dynamics_count_by_year.count_dict.keys()}
        self.dynamics_job_count_city.percentage()
        return self

    def print_result(self):
        """Печатает результат анализа данных

        """
        dynamics_salary_by_year = self.dynamics_salary_by_year.average_salary()
        dynamics_count_by_year = self.dynamics_count_by_year.count_dict
        dynamics_job_salary_year = self.dynamics_job_salary_year.average_salary()
        dynamics_job_count_year = self.dynamics_job_count_year.count_dict
        dynamics_job_salary_city = self.dynamics_job_salary_city.top_salary(self.dynamics_job_count_city.city_list)
        dynamics_job_count_city = self.dynamics_job_count_city.top_percentage_dict
        print(f"Динамика уровня зарплат по годам: "
              f"{dynamics_salary_by_year}")
        print(f"Динамика количества вакансий по годам: "
              f"{dynamics_count_by_year}")
        print(f"Динамика уровня зарплат по годам для выбранной профессии: "
              f"{dynamics_job_salary_year}")
        print(f"Динамика количества вакансий по годам для выбранной профессии: "
              f"{dynamics_job_count_year}")
        print(f"Уровень зарплат по городам (в порядке убывания): "
              f"{dynamics_job_salary_city}")
        print(f"Доля вакансий по городам (в порядке убывания): "
              f"{dynamics_job_count_city}")
        Report(self.job_name, dynamics_salary_by_year, dynamics_count_by_year, dynamics_job_salary_year,
               dynamics_job_count_year, dynamics_job_salary_city, dynamics_job_count_city).generate_pdf()


class Report():
    """Класс для представления отчета по анализу вакансий
    Attributes:
        job_name (str): Название вводимой профессии
        dynamics_salary_by_year (dict): Словарь оклад:год
        dynamics_count_by_year (dict): Словарь колличества оклад:год
        dynamics_job_salary_year (dict): Словарь работа:год
        dynamics_job_count_year (dict):Словарь колличества оработа:год
        dynamics_job_salary_city (dict): Словарь работа:город
        dynamics_job_count_city (dict):Словарь колличества работа:город
        tab_first (list): Первая таблица
        tab_second (list): Вторая таблица
        tab_third (list): Третья таблица
    """
    def __init__(self, job_name, dynamics_salary_by_year, dynamics_count_by_year, dynamics_job_salary_year,
                 dynamics_job_count_year, dynamics_job_salary_city, dynamics_job_count_city):
        """ Инициализация объектов Report

        Args:
            job_name (str): Название вводимой профессии
            dynamics_salary_by_year (dict): Словарь оклад:год
            dynamics_count_by_year (dict): Словарь колличества оклад:год
            dynamics_job_salary_year (dict): Словарь работа:год
            dynamics_job_count_year (dict):Словарь колличества оработа:год
            dynamics_job_salary_city (dict): Словарь работа:город
            dynamics_job_count_city (dict):Словарь колличества работа:город
        """
        self.job_name = job_name
        self.dynamics_salary_by_year = dynamics_salary_by_year
        self.dynamics_count_by_year = dynamics_count_by_year
        self.dynamics_job_salary_year = dynamics_job_salary_year
        self.dynamics_job_count_year = dynamics_job_count_year
        self.dynamics_job_salary_city = dynamics_job_salary_city
        self.dynamics_job_count_city = dynamics_job_count_city
        self.tab_first = []
        self.tab_second = []
        self.tab_third = []

    def generate_excel(self):
        """Генерирует эксель-файл

        """
        wb = openpyxl.Workbook()
        wb.active.title = 'Статистика по годам'
        wb.create_sheet('Статистика по городам')
        border = Side(style='thin', color='000000')
        ns_border = NamedStyle(name='cell',
                               border=Border(left=border, top=border, right=border, bottom=border))
        ns_header = NamedStyle(name='header',
                               border=Border(left=border, top=border, right=border, bottom=border),
                               font=Font(bold=True))
        wb.add_named_style(ns_header)
        wb.add_named_style(ns_border)
        year_sheet = wb['Статистика по годам']
        headers = ['Год', 'Средняя зарплата', f'Средняя зарплата - {self.job_name}',
                   'Количество вакансий', f'Количество вакансий - {self.job_name}']
        self.tab_first.append(headers)
        year_sheet.append(headers)
        for year, value in self.dynamics_salary_by_year.items():
            line = [year, value, self.dynamics_job_salary_year[year], self.dynamics_count_by_year[year], self.dynamics_job_count_year[year]]
            self.tab_first.append(line)
            year_sheet.append(line)
        dims = {}
        for row in year_sheet.rows:
            for cell in row:
                dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))
                cell.style = 'cell'
        for column, value in dims.items():
            if value > 0:
                year_sheet[f'{column}1'].style = 'header'
            year_sheet.column_dimensions[column].width = value + 2

        year_city = wb['Статистика по городам']
        headers_second = ['Город', 'Уровень зарплат', '', 'Город', 'Доля вакансий']
        self.tab_second.append(headers_second[:2])
        self.tab_third.append(headers_second[3:])
        year_city.append(headers_second)
        a = iter(self.dynamics_job_count_city)
        for city, value in self.dynamics_job_salary_city.items():
            city_count = next(a)
            line_first = [city, value]
            line_second = [city_count, self.dynamics_job_count_city[city_count]]
            year_city.append([*line_first, '', *line_second])
            self.tab_second.append(line_first)
            self.tab_third.append(line_second)
        dims = {}
        for row in year_city.rows:
            for cell in row:
                if cell.value != '':
                    dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))
                    cell.style = 'cell'
                else:
                    dims[cell.column_letter] = 0
                if cell.column_letter == 'E':
                    cell.number_format = '0.00%'
        for column, value in dims.items():
            if value > 0:
                year_city[f'{column}1'].style = 'header'
            year_city.column_dimensions[column].width = value + 2

        wb.save('report.xlsx')

    def generate_pdf(self):
        """Метод для генерации pdf файла

        """
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("pdf_template.html")
        self.generate_excel()
        pdf_template = template.render({
            'image': 'graph.png',
            'first_table': self.tab_first[1:],
            'first_table_header': self.tab_first[0],
            'second_table': self.tab_second[1:],
            'second_table_header': self.tab_second[0],
            'third_table': list(
                map(lambda cell: (cell[0], '{:.2f}%'.format(cell[1] * 100).replace('.', ',')), self.tab_third[1:])),
            'third_table_header': self.tab_third[0],
            'job_name': self.job_name
        })
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options={"enable-local-file-access": ""})

    def generate_image(self):
        """Метод для генерации изображения требуемых графиков

        """
        graph = plt.figure()
        x_nums = np.arange(len(self.dynamics_salary_by_year.keys()))
        width = 0.4
        graph1 = graph.add_subplot(221)
        graph1.set_title('Уровень зарплат по годам')
        graph1.bar(x_nums - width / 2, self.dynamics_salary_by_year.values(), width, label='средняя з/п')
        graph1.bar(x_nums + width / 2, self.dynamics_job_salary_year.values(), width,
                   label=f'з/п {self.job_name}')
        graph1.set_xticks(x_nums, self.dynamics_salary_by_year.keys(), rotation='vertical')
        graph1.tick_params(axis='both', labelsize=8)
        graph1.grid(True, axis='y')
        graph1.legend(fontsize=8)

        graph2 = graph.add_subplot(222)
        graph2.set_title('Количество вакансий по годам')
        graph2.bar(x_nums - width / 2, self.dynamics_count_by_year.values(), width, label='Количество вакансий')
        graph2.bar(x_nums + width / 2, self.dynamics_job_count_year.values(), width,
                   label=f'Количество вакансий \n{self.job_name}')
        graph2.set_xticks(x_nums, self.dynamics_count_by_year.keys(), rotation='vertical')
        graph2.tick_params(axis='both', labelsize=8)
        graph2.grid(True, axis='y')
        graph2.legend(fontsize=8)

        y_cities = np.arange(len(self.dynamics_job_salary_city.keys()))
        graph3 = graph.add_subplot(223)
        graph3.set_title('Уровень зарплат по годам')
        graph3.barh(y_cities, self.dynamics_job_salary_city.values(), 0.8, align='center')
        keys = []
        for key in self.dynamics_job_salary_city.keys():
            if key.__contains__('-') or key.__contains__(' '):
                keys.append(key.replace('-', '-\n').replace(' ', '\n'))
            else:
                keys.append(key)
        graph3.set_yticks(y_cities, keys)
        graph3.invert_yaxis()
        graph3.grid(True, axis='x')
        graph3.tick_params(axis='x', labelsize=8)
        graph3.tick_params(axis='y', labelsize=6)

        graph4 = graph.add_subplot(224)
        graph4.set_title('Уровень зарплат по годам')
        city_stat = {'Другое': 1 - sum(self.dynamics_job_count_city.values())}
        for key, value in dict(self.dynamics_job_count_city).items():
            city_stat[key] = value
        graph4.pie(city_stat.values(), labels=city_stat.keys(), textprops={'fontsize': 6}, radius=1.1)
        plt.tight_layout()
        plt.savefig('graph.png')


def csv_reader(file_name):
    """Производит чтение файла

    Args:
        file_name (str): Название файла

    Return:
        list: Возвращает список словарей с вакансиями
    """
    global headers, lines
    reader = csv.reader(open(file_name, encoding="utf_8_sig"))
    try:
        headers = next(reader)
    except:
        quick_quit('Пустой файл')
    try:
        lines = [line for line in reader]
    except:
        quick_quit('Нет данных')
    return [dict(zip(headers, line)) for line in csv_filer(lines, headers)]


def csv_filer(lines, headers):
    """Заполняет список вакансиями

    Args:
        lines (list): Список вакансий
        headers (list): Список заголовков

    Returns:
        list: Возвращает корректный список вакансий
    """
    ans = []
    for line in lines:
        if len(line) == len(headers) and line.count('') == 0:
            ans.append(line)
    return ans


def quick_quit(message):
    """Метод для выдачи ошибки и выхода из программы.

    Args:
        message (str): Текст сообщение об ошибке
    """
    print(message)
    exit()


def pdf_create():
    """Метод для создания pdf файла, вызывая другие методы.

    """
    file_name = input("Введите название файла: ")
    job = input("Введите название профессии: ")
    data = csv_reader(file_name)
    if data is not None:
        Total().get_data([Vacancy(i) for i in data], job).print_result()