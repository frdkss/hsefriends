import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta
import os
from collections import Counter
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator

# Подключение к базе данных
db_path = r'D:\python_proj\hsefriends\database\accounts.db'

# Установим фиксированную начальную дату
fixed_start_date = datetime(2024, 10, 16)


def generate_reg_statistic(days=7):  # Для статистики за неделю указываем 7 дней
    # Определение временных рамок
    end_date = fixed_start_date + timedelta(days=days)  # Конечная дата на основе фиксированной начальной даты

    # Открытие соединения с базой данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL-запрос для получения времени регистрации
    cursor.execute("""
        SELECT registration_time FROM Accounts
        WHERE registration_time BETWEEN ? AND ?
    """, (fixed_start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')))

    registrations = cursor.fetchall()
    conn.close()

    # Обработка данных
    dates = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f').date() for row in registrations]

    # Подсчёт регистраций по дням
    date_count = Counter(dates)
    sorted_dates = sorted(date_count.keys())
    counts = [date_count[date] for date in sorted_dates]

    # Создание списка всех дат в диапазоне
    all_dates = [fixed_start_date.date() + timedelta(days=i) for i in range((end_date - fixed_start_date).days + 1)]

    # Построение графика с указанным размером
    plt.figure(figsize=(19.2, 10.8), dpi=100)
    plt.plot(sorted_dates, counts, marker='o', linestyle='-', color='b')
    plt.title(f'Registration Dynamics (From {fixed_start_date.strftime("%d.%m.%Y")} for {days} Days)')
    plt.xlabel('Date')
    plt.ylabel('Number of Registrations')
    plt.grid(True)

    # Форматирование дат на оси X
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))

    # Установка делений по оси X для отображения всех дат
    plt.gca().set_xticks(all_dates)
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())  # Обновляем локатор для отображения всех дат

    # Настройка делений по оси Y
    plt.gca().yaxis.set_major_locator(MultipleLocator(5))  # Основные деления каждые 5 единиц
    plt.gca().yaxis.set_minor_locator(MultipleLocator(1))  # Маленькие деления каждое равно 1

    # Сохранение графика
    os.makedirs('statistic_png/reg_stat', exist_ok=True)
    plt.savefig(f'statistic_png/reg_stat/reg_statistic_from_{fixed_start_date.strftime("%d.%m")}_for_{days}_days.png')
    plt.close()


# Пример вызова функции для статистики за неделю
generate_reg_statistic(days=7)
