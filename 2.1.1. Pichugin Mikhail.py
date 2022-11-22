import csv
import openpyxl
import openpyxl.styles.numbers
from openpyxl.styles import NamedStyle, Border, Side, Font
from datetime import datetime
from statistics import mean


class SalaryDict:
    def __init__(self):
        self.salary_dictionary = {}
        self.__average_salary_dictionary = {}

    def add(self, key, salary):
        if self.salary_dictionary.get(key) is None:
            self.salary_dictionary[key] = []
        return self.salary_dictionary[key].append(salary)

    def average_salary(self):
        for key, value in self.salary_dictionary.items():
            self.__average_salary_dictionary[key] = int(mean(value))
        return self.__average_salary_dictionary

    def top_salary(self, top_cities):
        self.average_salary()
        sorted_dictionary = dict(sorted(self.__average_salary_dictionary.items(), key=lambda x: x[1], reverse=True))
        top_salary_dictionary = {}
        for key, value in sorted_dictionary.items():
            if key in top_cities:
                top_salary_dictionary[key] = value
        return {x: top_salary_dictionary[x] for x in list(top_salary_dictionary)[:10]}


class CountDict:
    def __init__(self):
        self.length = 0
        self.count_dict = {}
        self.city_list = []
        self.top_percentage_dict = {}

    def add(self, key):
        if self.count_dict.get(key) is None:
            self.count_dict[key] = 0
        self.count_dict[key] += 1
        self.length += 1

    def percentage(self):
        percentage_dict = {}
        for key, value in self.count_dict.items():
            percentage = value / self.length
            if percentage >= 0.01:
                self.city_list.append(key)
                percentage_dict[key] = round(percentage, 4)
        sort_dict = dict(sorted(percentage_dict.items(), key=lambda x: x[1], reverse=True))
        self.top_percentage_dict = {x: sort_dict[x] for x in list(sort_dict)[:10]}


class Vacancy:
    def __init__(self, fields):
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
    def __init__(self):
        self.dynamics_salary_by_year = SalaryDict()
        self.dynamics_count_by_year = CountDict()
        self.dynamics_job_salary_year = SalaryDict()
        self.dynamics_job_count_year = CountDict()
        self.dynamics_job_salary_city = SalaryDict()
        self.dynamics_job_count_city = CountDict()

    def get_data(self, vacancies, job_name):
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
               dynamics_job_count_year, dynamics_job_salary_city, dynamics_job_count_city).generate_excel()


class Report:
    def __init__(self, job_name, dynamics_salary_by_year, dynamics_count_by_year, dynamics_job_salary_year,
                 dynamics_job_count_year, dynamics_job_salary_city, dynamics_job_count_city):
        self.job_name = job_name
        self.dynamics_salary_by_year = dynamics_salary_by_year
        self.dynamics_count_by_year = dynamics_count_by_year
        self.dynamics_job_salary_year = dynamics_job_salary_year
        self.dynamics_job_count_year = dynamics_job_count_year
        self.dynamics_job_salary_city = dynamics_job_salary_city
        self.dynamics_job_count_city = dynamics_job_count_city

    def generate_excel(self):
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
        year_sheet.append(['Год', 'Средняя зарплата', f'Средняя зарплата - {self.job_name}',
                           'Количество вакансий', f'Количество вакансий - {self.job_name}'])
        for year, value in self.dynamics_salary_by_year.items():
            year_sheet.append(
                [year, value, self.dynamics_job_salary_year[year], self.dynamics_count_by_year[year],
                 self.dynamics_job_count_year[year]])
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
        year_city.append(['Город', 'Уровень зарплат', '', 'Город', 'Доля вакансий'])
        a = iter(self.dynamics_job_count_city)
        for city, value in self.dynamics_job_salary_city.items():
            city_count = next(a)
            year_city.append([city, value, '', city_count, self.dynamics_job_count_city[city_count]])
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


def csv_reader(file_name):
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
    ans = []
    for line in lines:
        if len(line) == len(headers) and line.count('') == 0:
            ans.append(line)
    return ans


def quick_quit(message):
    print(message)
    exit()


file_name = input("Введите название файла: ")
job = input("Введите название профессии: ")
data = csv_reader(file_name)
if data is not None:
    Total().get_data([Vacancy(i) for i in data], job).print_result()