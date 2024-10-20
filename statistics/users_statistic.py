import matplotlib.pyplot as plt
import sqlite3
import os
from matplotlib.ticker import MultipleLocator

# Подключение к базе данных
db_path = r'D:\python_proj\hsefriends\database\accounts.db'

def generate_users_statistic():
    # Открытие соединения с базой данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL-запрос для подсчета общего количества пользователей
    cursor.execute("SELECT COUNT(*) FROM Accounts")
    total_users = cursor.fetchone()[0]
    conn.close()

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
    os.makedirs('statistic_png/user_stat', exist_ok=True)
    plt.savefig('statistic_png/user_stat/users_statistic.png')
    plt.close()

# Пример вызова функции
generate_users_statistic()
