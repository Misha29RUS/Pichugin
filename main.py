import PdfCreate
import TableCreate


def Creator():
    input_person = input("Введите формат таблицы(Вакансии/Статистика): ")
    if input_person == "Статистика":
        PdfCreate.pdf_create()
    elif input_person == "Вакансии":
        TableCreate.table_create()
    else:
        print("Данные не корректны")
        exit()


Creator()
