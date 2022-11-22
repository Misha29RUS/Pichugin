import datetime
import os
from prettytable import PrettyTable
import csv
import re

experience_sort = {
    'Нет опыта': 0,
    'От 1 года до 3 лет': 1,
    'От 3 до 6 лет': 2,
    'Более 6 лет': 3
}

experience = {
    'noExperience': "Нет опыта",
    'between1And3': "От 1 года до 3 лет",
    'between3And6': "От 3 до 6 лет",
    'moreThan6': "Более 6 лет"
}

premium = {
    'False': "Нет",
    'True': "Да"
}

currency = {
    'AZN': "Манаты",
    'BYR': "Белорусские рубли",
    'EUR': "Евро",
    'GEL': "Грузинский лари",
    'KGS': "Киргизский сом",
    'KZT': "Тенге",
    'RUR': "Рубли",
    'UAH': "Гривны",
    'USD': "Доллары",
    'UZS': "Узбекский сум",
}

sal_gross = {
    'False': "С вычетом налогов",
    'True': "Без вычета налогов"
}

currency_to_rub = {
    "Манаты": 35.68,
    "Белорусские рубли": 23.91,
    "Евро": 59.90,
    "Грузинский лари": 21.74,
    "Киргизский сом": 0.76,
    "Тенге": 0.13,
    "Рубли": 1,
    "Гривны": 1.64,
    "Доллары": 60.66,
    "Узбекский сум": 0.0055,
}

translator = {
    'Название': 'name',
    'Описание': 'description',
    'Навыки': 'key_skills',
    'Опыт работы': 'experience_id',
    'Премиум-вакансия': 'premium',
    'Компания': 'employer_name',
    'Оклад': 'salary',
    'Верхняя граница вилки оклада': 'salary_to',
    'Нижняя граница вилки оклада': 'salary_from',
    'Оклад указан до вычета налогов': 'salary_gross',
    'Идентификатор валюты оклада': 'salary_currency',
    'Название региона': 'area_name',
    'Дата публикации вакансии': 'published_at',
}


class UserInput:
    sort_phrases = ["Название", "Описание", "Навыки", "Опыт работы",
                    "Премиум-вакансия", "Компания", "Оклад", "Название региона", "Дата публикации вакансии", "Идентификатор валюты оклада"]

    def __init__(self):
        self.file_name = input("Введите название файла: ")
        self.filter_param = input("Введите параметр фильтрации: ")
        self.sort_param = input("Введите параметр сортировки: ")
        self.reverse_sort_param = input("Обратный порядок сортировки (Да / Нет): ")
        self.distance_param = input("Введите диапазон вывода: ").split()
        self.columns_param = self.check_names(input("Введите требуемые столбцы: ").split(", "))
        self.filter_param = self.check_filter_param(self.filter_param)
        self.sort_param = self.check_sort_param(self.sort_param)
        self.reverse_sort_param = self.check_reverse_sort_param(self.reverse_sort_param)

    def check_filter_param(self, filter_param):
        if filter_param != "" and ": " not in filter_param:
            quick_quit("Формат ввода некорректен")

        if filter_param != "" and filter_param.split(": ")[0] not in self.sort_phrases:
            quick_quit("Параметр поиска некорректен")
        return filter_param

    def check_sort_param(self, sort_param):
        if sort_param != "" and sort_param not in self.sort_phrases:
            quick_quit("Параметр сортировки некорректен")
        return sort_param

    @staticmethod
    def check_reverse_sort_param(reverse_sort_param):
        if reverse_sort_param not in ["Да", "Нет", ""]:
            quick_quit("Порядок сортировки задан некорректно")
        return reverse_sort_param == "Да"

    @staticmethod
    def check_names(headers):
        if "" in headers:
            headers = ["Название", "Описание", "Навыки", "Опыт работы",
                     "Премиум-вакансия", "Компания", "Оклад", "Название региона", "Дата публикации вакансии"]
        headers.insert(0, "№")
        return headers


class DataSet:
    def __init__(self, file_name):
        if os.stat(file_name).st_size == 0:
            quick_quit("Пустой файл")
        self.data = [row for row in csv.reader(open(file_name, encoding="utf_8_sig"))]
        self.names = self.data[0]
        self.all_data = [row for row in self.data[1:] if len(row) == len(self.names) and row.count("") == 0]
        if len(self.all_data) == 0:
            quick_quit("Нет данных")


class Vacancy:
    def __init__(self, pers_data):
        self.name = str
        self.description = str
        self.key_skills = str or list
        self.experience_id = str
        self.premium = str
        self.employer_name = str
        self.salary_from = str
        self.salary_to = str
        self.salary_gross = str
        self.salary_currency = str
        self.area_name = str
        self.full_published_time = str
        self.published_at = str
        self.salary = str
        for key, value in pers_data.items():
            self.__setattr__(key, self.formatter(key, value))

        self.salary = f'{self.salary_from} - {self.salary_to} ({self.salary_currency}) ({self.salary_gross})'

    def formatter(self, key, value):
        if key == "key_skills" and type(value) == list:
            return "\n".join(value)
        elif key == "premium":
            return premium[value]
        elif key == "salary_gross":
            return sal_gross[value]
        elif key == "experience_id":
            return experience[value]
        elif key == "salary_currency":
            return currency[value]
        elif key == "salary_to" or key == "salary_from":
            return "{:,}".format(int(float(value))).replace(",", " ")
        elif key == "published_at":
            self.full_published_time = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").strftime("%d.%m.%Y-%H"
                                                                                                         ":%M:%S")
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z").strftime("%d.%m.%Y")
        else:
            return value

    def filter_condition(self, filter_param):
        if filter_param == "":
            return True
        key, value = filter_param.split(": ")
        if key == "Оклад":
            return float(self.salary_from.replace(' ', '')) <= float(value) <= float(self.salary_to.replace(" ", ""))
        elif key == "Идентификатор валюты оклада":
            return self.salary_currency == value
        elif key == "Навыки":
            for skill in value.split(", "):
                if skill not in self.key_skills.split("\n"):
                    return False
            return True
        else:
            return self.__dict__[translator[key]] == value


class Table:
    def __init__(self):
        self.table = PrettyTable(["№", "Название", "Описание", "Навыки", "Опыт работы", "Премиум-вакансия",
                                  "Компания", "Оклад", "Название региона", "Дата публикации вакансии"])
        self.table.hrules = 1
        self.table.align = "l"
        self.table.max_width = 20

    def print(self, all_data, start, end, list_names):
        for index, data in enumerate(all_data):
            row = [index + 1]
            for name in self.table.field_names[1:]:
                data_value = data.__dict__[translator[name]]
                if len(data_value) > 100:
                    data_value = data_value[:100] + "..."
                row.append(data_value)
            self.table.add_row(row)
        print(self.table.get_string(start=start, end=end, fields=list_names))


def get_vacancies(all_data, filter_param, sort_param, reverse_sort_param):
    data = []
    for pers_data in all_data:
        parsed_data = Vacancy(dict(zip(names, map(parse_html, pers_data))))
        if parsed_data.filter_condition(filter_param):
            data.append(parsed_data)
    return sort_vacancies(data, sort_param, reverse_sort_param)


def sort_vacancies(all_data, sort_param, reverse_sort_param):
    if sort_param == "":
        return all_data

    return sorted(all_data, key=lambda data: get_sort_func(data, sort_param), reverse=reverse_sort_param)


def get_sort_func(data, sort_param):
    if sort_param == "Навыки":
        return len(data.key_skills.split("\n"))
    elif sort_param == "Оклад":
        return currency_to_rub[data.salary_currency] * \
               (float(data.salary_from.replace(" ", "")) + float(data.salary_to.replace(" ", ''))) // 2
    elif sort_param == "Дата публикации вакансии":
        return data.full_published_time
    elif sort_param == "Опыт работы":
        return experience_sort[data.experience_id]
    else:
        return data.__getattribute__(translator[sort_param])


def parse_html(value):
    result = [" ".join(word.split()) for word in re.sub("<.*?>", "", value).replace("\r\n", "\n").split('\n')]
    if len(result) == 1:
        return result[0]
    return result


def print_vacancies(all_data, distance, columns):
    if len(all_data) == 0:
        quick_quit("Ничего не найдено")
    if len(distance) >= 1:
        start = int(distance[0]) - 1
    else:
        start = 0
    if len(distance) >= 2:
        end = int(distance[1]) - 1
    else:
        end = len(all_data)
    table = Table()
    table.print(all_data, start, end, columns)


def quick_quit(message):
    print(message)
    exit()


def table_create():
    inputed = UserInput()
    dataset = DataSet(inputed.file_name)
    (names, all_vac_data) = dataset.names, dataset.all_data
    data = get_vacancies(all_vac_data, inputed.filter_param, inputed.sort_param, inputed.reverse_sort_param)
    print_vacancies(data, inputed.distance_param, inputed.columns_param)


