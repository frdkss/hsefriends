import matplotlib.pyplot as plt
import sqlite3
import os
from collections import Counter
from matplotlib.ticker import MultipleLocator


def generate_age_statistic(db_path, stat_path):
    # Открытие соединения с базой данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL-запрос для получения возраста пользователей
    cursor.execute("SELECT age FROM Accounts")
    ages = cursor.fetchall()
    conn.close()

    # Обработка данных
    age_list = [row[0] for row in ages if row[0] is not None]  # Игнорируем None значения
    age_count = Counter(age_list)
    total_users = sum(age_count.values())

    # Подсчет статистики
    users_above_18 = sum(1 for age in age_list if age > 18)
    percent_above_18 = (users_above_18 / total_users * 100) if total_users > 0 else 0

    # Создание папки для статистики, если она не существует
    os.makedirs(stat_path, exist_ok=True)

    # Запись статистики в файл
    with open(f'{stat_path}age_statistic.txt', 'w') as f:
        f.write(f"Процент людей старше 18 лет: {percent_above_18:.2f}%\n")
        for age in range(min(age_count.keys()), max(age_count.keys()) + 1):
            if age_count[age] > 0:  # Исключаем возраста с нулевым количеством пользователей
                percent = (age_count[age] / total_users * 100) if total_users > 0 else 0
                f.write(f"Возраст {age}: {percent:.2f}%\n")

    # Построение столбчатой диаграммы
    sorted_ages = list(range(min(age_count.keys()), max(age_count.keys()) + 1))
    counts = [age_count.get(age, 0) for age in sorted_ages]  # Используем 0, если возраста нет

    plt.figure(figsize=(19.2, 10.8), dpi=100)
    plt.bar(sorted_ages, counts, color='b', width=0.8)  # Столбчатая диаграмма
    plt.title('Age Distribution of Users')
    plt.xlabel('Age')
    plt.ylabel('Number of Users')
    plt.grid(axis='y')

    # Настройка делений по оси X для каждого возраста
    plt.xticks(sorted_ages)  # Устанавливаем метки для каждого года
    plt.gca().xaxis.set_minor_locator(MultipleLocator(1))  # Маленькие деления каждое равно 1

    # Настройка делений по оси Y
    plt.gca().yaxis.set_major_locator(MultipleLocator(5))  # Основные деления каждые 5 единиц
    plt.gca().yaxis.set_minor_locator(MultipleLocator(1))  # Маленькие деления каждое равно 1

    # Сохранение диаграммы
    plt.savefig(f'{stat_path}age_statistic.png')
    plt.close()
