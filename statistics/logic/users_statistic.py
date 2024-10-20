import matplotlib.pyplot as plt
import sqlite3
import os
from matplotlib.ticker import MultipleLocator


def generate_users_statistic(db_path, stat_path):
    # Открытие соединения с базой данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL-запрос для подсчета общего количества пользователей
    cursor.execute("SELECT COUNT(*) FROM Accounts")
    total_users = cursor.fetchone()[0]
    conn.close()

    # Запись количества пользователей в текстовый файл
    with open(f'{stat_path}users_count.txt', 'w') as f:
        f.write(f'Количество пользователей: {total_users}\n')

    # Построение графика
    plt.figure(figsize=(19.2, 10.8), dpi=100)
    plt.bar(['Total Users'], [total_users], color='g')
    plt.title('Total Number of Users')
    plt.ylabel('Number of Users')
    plt.grid(True)

    # Настройка делений по оси Y
    plt.gca().yaxis.set_major_locator(MultipleLocator(5))  # Основные деления каждые 5 единиц
    plt.gca().yaxis.set_minor_locator(MultipleLocator(1))  # Маленькие деления каждое равно 1

    # Сохранение графика
    os.makedirs(stat_path, exist_ok=True)
    plt.savefig(f'{stat_path}users_statistic.png')
    plt.close()

