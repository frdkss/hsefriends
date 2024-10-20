import matplotlib.pyplot as plt
import sqlite3
import os
from collections import Counter
from matplotlib.ticker import MultipleLocator

# Подключение к базе данных
db_path = r'D:\python_proj\hsefriends\database\accounts.db'

def generate_sex_statistic():
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
    os.makedirs('statistic_png/sex_stat', exist_ok=True)
    plt.savefig('statistic_png/sex_stat/sex_statistic.png')
    plt.close()

# Пример вызова функции
generate_sex_statistic()
