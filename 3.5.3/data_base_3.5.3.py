import sqlite3
import pandas as pd

vacancy = f"%{input('Введите название профессии: ')}%"
connect = sqlite3.connect("data_base_3.5.2.sqlite")
cursor = connect.cursor()
len_database = pd.read_sql("select count(*) from 'data_base_3.5.2.sqlite'", connect).to_dict()["count(*)"][0]

groups_for_year_name_salary = pd.read_sql("select substr(published_at, 1, 4) as year, round(avg(salary)) from 'data_base_3.5.2.sqlite' where name like :vacancy group by year", connect, params=[vacancy])
dict_for_year_name_salary = dict(groups_for_year_name_salary[["year", "round(avg(salary))"]].to_dict("split")["data"])

groups_for_year_salary = pd.read_sql("select substr(published_at, 1, 4) as year, round(avg(salary)) from 'data_base_3.5.2.sqlite' group by year", connect)
dict_for_year_salary = dict(groups_for_year_salary[["year", "round(avg(salary))"]].to_dict("split")["data"])

groups_for_year_vacancy = pd.read_sql("select substr(published_at, 1, 4) as year, count(name) from 'data_base_3.5.2.sqlite' group by year", connect)
dict_for_year_vacancy = dict(groups_for_year_vacancy[["year", "count(name)"]].to_dict("split")["data"])

groups_for_year_name_vacancy = pd.read_sql("select substr(published_at, 1, 4) as year, count(name) from 'data_base_3.5.2.sqlite' where name like :vacancy group by year", connect, params=[vacancy])
dict_for_year_name_vacancy = dict(groups_for_year_name_vacancy[["year", "count(name)"]].to_dict("split")["data"])


def get_sorted_for_area_dict(start_dict):
    """ Метод для сортировки словаря по городам вакансии
    Args:
        start_dict (dict): Начальный словарь
    Returns:
        dict: Возвращает отсортированный словарь
    """
    sorted_tuples = sorted(start_dict.items(), key=lambda item: item[1], reverse=True)[:10]
    sorted_dict = {key: value for key, value in sorted_tuples}
    return sorted_dict


groups_for_area_vacancy = pd.read_sql("select area_name, count(area_name) from 'data_base_3.5.2.sqlite' group by area_name order by count(area_name) desc limit 10", connect)
groups_for_area_vacancy["count(area_name)"] = round(groups_for_area_vacancy["count(area_name)"] / len_database, 2)
dict_for_area_vacancy = dict(groups_for_area_vacancy[["area_name", 'count(area_name)']].to_dict("split")["data"])

groups_for_area_salary = pd.read_sql("select area_name, round(avg(salary)), count(area_name) from 'data_base_3.5.2.sqlite' group by area_name order by count(area_name) desc ", connect)
groups_for_area_salary = groups_for_area_salary[groups_for_area_salary["count(area_name)"] >= 0.01 * len_database]
dict_for_area_salary = get_sorted_for_area_dict(dict(groups_for_area_salary[["area_name", "round(avg(salary))"]].to_dict("split")["data"]))

print("Динамика уровня зарплат по годам:", dict_for_year_salary)
print("Динамика количества вакансий по годам:", dict_for_year_vacancy)
print("Динамика уровня зарплат по годам для выбранной профессии:", dict_for_year_name_salary)
print("Динамика количества вакансий по годам для выбранной профессии:", dict_for_year_name_vacancy)
print("Уровень зарплат по городам (в порядке убывания):", dict_for_area_salary)
print("Доля вакансий по городам (в порядке убывания):", dict_for_area_vacancy)