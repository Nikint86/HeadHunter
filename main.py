import requests
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable


def predict_rub_salary_hh(vacancy):
    vacancy_salary_info = vacancy.get('salary')
    if vacancy_salary_info:
        salary_from = vacancy_salary_info.get('from')
        salary_to = vacancy_salary_info.get('to')
        if salary_from:
            return float(salary_from)
        if salary_to:
            return float(salary_to)
    return None


def predict_rub_salary_superjob(vacancy):
    salary_from = vacancy.get('payment_from')
    salary_to = vacancy.get('payment_to')
    if salary_from:
        return float(salary_from)
    if salary_to:
        return float(salary_to)
    return None


def get_statistics_hh():
    moscow = 1
    vacancies_per_page = 100
    url = "https://api.hh.ru/vacancies"
    programming_languages = ["Python", "C", "C++", "Java", "JavaScript", "Scala", "Ruby", "Swift"]
    hh_vacancies = {}

    for language in programming_languages:
        params = {
            "text": f"Программист {language}",
            "area": moscow,
            "per_page": vacancies_per_page,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        vacancies_hh = response.json()
        salaries = []

        for vacancy in vacancies_hh['items']:
            salary = predict_rub_salary_hh(vacancy)
            if salary:
                salaries.append(salary)

        average_salary = int(sum(salaries) / len(salaries)) if salaries else 0
        hh_vacancies[language] = {
            "vacancies_found": vacancies_hh['found'],
            "vacancies_processed": len(salaries),
            "average_salary": average_salary
        }

    return hh_vacancies


def get_vacancies_superjob(api_app_id):
    url = "https://api.superjob.ru/2.0/vacancies/"
    programming_languages = ["Python", "C", "C++", "Java", "JavaScript", "Scala", "Ruby", "Swift"]
    superjob_vacancies = {}

    for language in programming_languages:
        params = {
            "keyword": f"Программист {language}",
            "town": "Москва",
            "count": 100,
        }
        headers = {
            "X-Api-App-Id": api_app_id
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        vacancies_superjob = response.json()
        salaries = []

        for vacancy in vacancies_superjob['objects']:
            salary = predict_rub_salary_superjob(vacancy)
            if salary:
                salaries.append(salary)

        average_salary = int(sum(salaries) / len(salaries)) if salaries else 0
        superjob_vacancies[language] = {
            "vacancies_found": vacancies_superjob['total'],
            "vacancies_processed": len(salaries),
            "average_salary": average_salary
        }

    return superjob_vacancies


def print_results_table(results, title):
    table_data = [
        ["Язык программирования", "Найдено вакансий", "Обработано вакансий", "Средняя зарплата"]
    ]

    for language, vacancies_data in results.items():
        table_data.append([
            language,
            vacancies_data["vacancies_found"],
            vacancies_data["vacancies_processed"],
            vacancies_data["average_salary"]
        ])

    table = AsciiTable(table_data)
    table.title = title

    print(table.table)


def main():
    load_dotenv()

    api_app_id = os.environ.get("SUPERJOB_KEY")

    if api_app_id is None:
        return print("Неверный ключ superjob")

    hh_results = get_statistics_hh()
    sj_results = get_vacancies_superjob(api_app_id)

    print_results_table(hh_results, "Результаты hh.ru")
    print("\n")
    print_results_table(sj_results, "Результаты SuperJob")


if __name__ == "__main__":
    main()