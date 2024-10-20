import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime
import os
from collections import Counter
from matplotlib.ticker import MultipleLocator

# Подключение к базе данных
db_path = r'D:\python_proj\hsefriends\database\accounts.db'

def generate_age_statistic():
    # Открытие соединения с базой данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL-запрос для получения возраста пользователей
    cursor.execute("SELECT age FROM Accounts")
    ages = cursor.fetchall()
    conn.close()

    # Обработка данных
    age_list = [row[0] for row in ages]
    age_count = Counter(age_list)
    sorted_ages = sorted(age_count.keys())
    counts = [age_count[age] for age in sorted_ages]

    # Построение графика
    plt.figure(figsize=(19.2, 10.8), dpi=100)
    plt.bar(sorted_ages, counts, color='b', width=0.8)
    plt.title('Age Distribution of Users')
    plt.xlabel('Age')
    plt.ylabel('Number of Users')
    plt.grid(True)

    # Настройка делений по оси Y
    plt.gca().yaxis.set_major_locator(MultipleLocator(5))  # Основные деления каждые 5 единиц
    plt.gca().yaxis.set_minor_locator(MultipleLocator(1))  # Маленькие деления каждое равно 1

    # Сохранение графика
    os.makedirs('statistic_png/age_stat', exist_ok=True)
    plt.savefig('statistic_png/age_stat/age_statistic.png')
    plt.close()

# Пример вызова функции
generate_age_statistic()
