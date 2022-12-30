import pandas as pd
import requests
import concurrent.futures


class NewVacancies:
    """ Класс для получения вакансий через API hh.ru в формате .csv """
    @staticmethod
    def get_json(sets):
        """ Метод для запроса JSON-файла с данными о вакансиях с hh.ru
        Args:
            sets (list[dict]): Словарь с параметрами поиска
        Returns:
            list[dict] or list[dict[dict]]: Возвращает данные о вакансиях в формате JSON
        """
        return requests.get('https://api.hh.ru/vacancies', sets).json()["items"]

    @staticmethod
    def get_data(vacs):
        """ Метод для получения списка с данными о вакансиях из JSON файла
        Args:
            vacs(list[dict] or list[dict[dict]]): Список вакансий из JSON файла
        Returns:
            list[dict]: Возвращает список с вакансиями
        """
        return [[vac["name"], vac["salary"]["from"], vac["salary"]["to"], vac["salary"]["currency"],
                 vac["area"]["name"], vac["published_at"]] for vac in vacs if vac["salary"]]


if __name__ == "__main__":
    lists = 20
    set1 = [dict(specialization=1, date_from="2022-12-15T00:00:00", date_to="2022-12-15T12:00:00", per_page=100, page=page) for page in range(lists)]
    set2 = [dict(specialization=1, date_from="2022-12-15T12:00:00", date_to="2022-12-16T00:00:00", per_page=100, page=page) for page in range(lists)]
    parser = NewVacancies()
    executor = concurrent.futures.ProcessPoolExecutor()
    data = list(executor.map(parser.get_json, set1 + set2))
    answer = list(executor.map(parser.get_data, data))
    columns = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
    data = pd.concat([pd.DataFrame(x, columns=columns) for x in answer])
    data.to_csv("new_vacancies_hh.csv", index=False)