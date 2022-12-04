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
    """Класс пользовательского ввода
    Attributes:
        file_name (str): Название файла
        filter_param (str): Параметр фильтрации
        sort_param (str): Параметр сортировки
        reverse_sort_param (str): Обратная сортировка
        distance_param (str): Диапозон вывода
        columns_param (str): Столбцы вывода
    """
    sort_phrases = ["Название", "Описание", "Навыки", "Опыт работы",
                    "Премиум-вакансия", "Компания", "Оклад", "Название региона", "Дата публикации вакансии", "Идентификатор валюты оклада"]

    def __init__(self):
        """
        Инициализирует объекты UserInput
        """
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
        """Проверка параметра фильтрации
        Args:
            filter_param (str): Параметр фильтрации

        Returns:
            str: Текст ошибки или передаваемый параметр фильтрации, в случае отсутствия ошибки
        """
        if filter_param != "" and ": " not in filter_param:
            quick_quit("Формат ввода некорректен")

        if filter_param != "" and filter_param.split(": ")[0] not in self.sort_phrases:
            quick_quit("Параметр поиска некорректен")
        return filter_param

    def check_sort_param(self, sort_param):
        """Проверка параметра сортировки
        Args:
            sort_param (str): Параметр сортировки

        Returns:
            str: Текст ошибки или передаваемый параметр сортировки, в случае отсутствия ошибки
        """
        if sort_param != "" and sort_param not in self.sort_phrases:
            quick_quit("Параметр сортировки некорректен")
        return sort_param

    @staticmethod
    def check_reverse_sort_param(reverse_sort_param):
        """Проверка обратной сортировка
        Args:
            reverse_sort_param (str): Обратная сортировка

        Returns:
            str: Текст ошибки или передаваемый параметр обратной сортировки, в случае отсутствия ошибки
        """
        if reverse_sort_param not in ["Да", "Нет", ""]:
            quick_quit("Порядок сортировки задан некорректно")
        return reverse_sort_param == "Да"

    @staticmethod
    def check_names(headers):
        """ Проверка названий вводимых пользователем столбцов
        Args:
           headers (list): Список столбцов вывода

        Returns: Изменённые сталбцы(добавления столбца № перед всеми другими),в случае соответствии правилам ввода
        """
        if "" in headers:
            headers = ["Название", "Описание", "Навыки", "Опыт работы",
                     "Премиум-вакансия", "Компания", "Оклад", "Название региона", "Дата публикации вакансии"]
        headers.insert(0, "№")
        return headers


class DataSet:
    """Класс чтения и подготовки данных из CSV-файла
    Attributes:
        data (list): Все данные
        names (str): Заголовки
        all_data (list): Все вакансии
    """
    def __init__(self, file_name):
        """Проверяет пустоту файла и инициализирует объекты DataSet

        Args:
            file_name (str): Название файла

        """
        if os.stat(file_name).st_size == 0:
            quick_quit("Пустой файл")
        self.data = [row for row in csv.reader(open(file_name, encoding="utf_8_sig"))]
        self.names = self.data[0]
        self.all_data = [row for row in self.data[1:] if len(row) == len(self.names) and row.count("") == 0]
        if len(self.all_data) == 0:
            quick_quit("Нет данных")


class Vacancy:
    """ Класс установки всех основных полей вакансии
    Attributes:
        name (str): Название вакансии
        description (str): Описание вакансии
        key_skills (str or list): Навыки
        experience_id (str): Опыт работы
        premium (str): Премиум вакансия
        employer_name (str):
        salary_from (str): Нижняя граница зарплаты
        salary_to (str): Верхняя граница зарплаты
        salary_gross (str): Размер заработной платы до вычета всех налогов(да или нет)
        salary_currency (str): Валюта, в которой указана зарплата
        area_name (str): Название города
        full_published_time (str): Полное время публикации
        published_at (str):  Сокращённая дата публикации
        salary (str): Зарплата
    """
    def __init__(self, pers_data):
        """ Инициализирует объекты Vacancy

        Args:
            pers_data (dict): Данные по всем вакансиям
        """
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
        """ Метод для форматирования значения передоваемого ключа
        Args:
            key (str): Ключ
            value (str): Значение
        Returns:
            str: Отформатированные данные соответствующего ключа
        """
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
        """Метод для проверки соответствия параметру фильтрации
        Args:
            filter_param (str): Параметр фильтрации
        Returns:
            bool: Соответствует или нет(true or false)
        """
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
    """ Класс для фармирования и заполнения таблицы

    Attributes:
        table (dict): Шаблон таблицы
    """
    def __init__(self):
        """Инициализирует объекты Vacancy

        """
        self.table = PrettyTable(["№", "Название", "Описание", "Навыки", "Опыт работы", "Премиум-вакансия",
                                  "Компания", "Оклад", "Название региона", "Дата публикации вакансии"])
        self.table.hrules = 1
        self.table.align = "l"
        self.table.max_width = 20

    def print(self, all_data, start, end, list_names):
        """ Визуализация таблицы
        Args:
            all_data (list): Все вакансии
            start (int): Начала обрезки таблицы
            end (int): Конец обрезки таблицы
            list_names (list): Колонки таблицы
        """
        for index, data in enumerate(all_data):
            row = [index + 1]
            for name in self.table.field_names[1:]:
                data_value = data.__dict__[translator[name]]
                if len(data_value) > 100:
                    data_value = data_value[:100] + "..."
                row.append(data_value)
            self.table.add_row(row)
        print(self.table.get_string(start=start, end=end, fields=list_names))


def get_vacancies(all_data, filter_param, sort_param, reverse_sort_param, names):
    """ Метод получения вакансии
    Args:
        all_data (list): Все вакансии
        filter_param (str): Параметр фильтрации
        sort_param (str): Параметр сортировки
        reverse_sort_param (boll): Обратная сортировка
        names (list): Заголовки
    Returns:
        list: лист с вакансиями
    """
    data = []
    for pers_data in all_data:
        parsed_data = Vacancy(dict(zip(names, map(parse_html, pers_data))))
        if parsed_data.filter_condition(filter_param):
            data.append(parsed_data)
    return sort_vacancies(data, sort_param, reverse_sort_param)


def sort_vacancies(all_data, sort_param, reverse_sort_param):
    """Метод сортировки листа с вакансиями
    Args:
        all_data (list): Все вакансии
        sort_param (str): Параметр сортировки
        reverse_sort_param (bool): Обратная сортировка
    Returns:
        list: Отсортированный или неостсортированный лист с вакансиями
    """
    if sort_param == "":
        return all_data

    return sorted(all_data, key=lambda data: get_sort_func(data, sort_param), reverse=reverse_sort_param)


def get_sort_func(data, sort_param):
    """ Метод сортировки
    Args:
        data (Vacancy): Вакансия
        sort_param (str): Параметр сортировки
    """
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
    """ Метод отчистки от html
    Args:
        value (str): Значение
    """
    result = [" ".join(word.split()) for word in re.sub("<.*?>", "", value).replace("\r\n", "\n").split('\n')]
    if len(result) == 1:
        return result[0]
    return result


def print_vacancies(all_data, distance, columns):
    """ Метод печати вакансий
    Args:
        all_data (list): Все вакансии
        distance(list): Диапозон вывода
        columns (list): Колонки таблицы
    """
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
    """Метод для выдачи ошибки и выхода из программы.

    Args:
        message (str): Текст сообщение об ошибке
    """
    print(message)
    exit()


def table_create():
    """Метод вызова других методов для формирования таблицы

    """
    inputed = UserInput()
    dataset = DataSet(inputed.file_name)
    (names, all_vac_data) = dataset.names, dataset.all_data
    data = get_vacancies(all_vac_data, inputed.filter_param, inputed.sort_param, inputed.reverse_sort_param, names)
    print_vacancies(data, inputed.distance_param, inputed.columns_param)
