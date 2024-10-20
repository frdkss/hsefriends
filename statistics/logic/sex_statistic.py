import matplotlib.pyplot as plt
import sqlite3
import os
from collections import Counter
from matplotlib.ticker import MultipleLocator


def generate_sex_statistic(db_path, stat_path):
    # Открытие соединения с базой данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL-запрос для получения пола пользователей
    cursor.execute("SELECT isMale FROM Accounts")
    sexes = cursor.fetchall()
    conn.close()

    # Обработка данных
    sex_list = [row[0] for row in sexes]
    sex_count = Counter(sex_list)

    # Подсчет общего числа пользователей
    total_users = len(sex_list)
    if total_users > 0:
        male_percentage = (sex_count[True] / total_users) * 100
        female_percentage = (sex_count[False] / total_users) * 100
    else:
        male_percentage = female_percentage = 0

    # Сохранение статистики в текстовый файл
    with open(f'{stat_path}statistics.txt', 'w') as f:
        f.write(f"Процент мужчин: {male_percentage:.2f}%\n")
        f.write(f"Процент женщин: {female_percentage:.2f}%\n")

    # Подготовка данных для графика
    labels = ['Male', 'Female']
    counts = [sex_count[True], sex_count[False]]

    # Построение графика
    plt.figure(figsize=(19.2, 10.8), dpi=100)
    plt.bar(labels, counts, color=['b', 'r'])
    plt.title('Sex Distribution of Users')
    plt.xlabel('Sex')
    plt.ylabel('Number of Users')
    plt.grid(True)

    # Настройка делений по оси Y
    plt.gca().yaxis.set_major_locator(MultipleLocator(5))  # Основные деления каждые 5 единиц
    plt.gca().yaxis.set_minor_locator(MultipleLocator(1))  # Маленькие деления каждое равно 1

    # Сохранение графика
    os.makedirs(stat_path, exist_ok=True)
    plt.savefig(f'{stat_path}sex_statistic.png')
    plt.close()

