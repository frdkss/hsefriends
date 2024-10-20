import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta
import os
from collections import Counter
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator

# Установим фиксированную начальную дату
fixed_start_date = datetime(2024, 10, 16)


def generate_reg_statistic(db_path, stat_path, days=7):  # Для статистики за неделю указываем 7 дней
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
    os.makedirs(stat_path, exist_ok=True)
    plt.savefig(f'{stat_path}reg_statistic_from_{fixed_start_date.strftime("%d.%m")}_for_{days}_days.png')
    plt.close()


def write_registration_statistics(db_path, stat_path):
    # Открытие соединения с базой данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получение регистраций за 1 день
    cursor.execute("""
        SELECT COUNT(*) FROM Accounts
        WHERE registration_time >= ?
    """, (fixed_start_date.strftime('%Y-%m-%d %H:%M:%S'),))
    reg_today = cursor.fetchone()[0]

    # Запись в файл reg_for1_day.txt
    with open(f'{stat_path}reg_for1_day.txt', 'w') as f:
        f.write(f'Количество пользователей, зарегистрировавшихся сегодня: {reg_today}\n')

    # Получение регистраций за 7 дней
    end_date_7_days = fixed_start_date + timedelta(days=7)
    cursor.execute("""
        SELECT registration_time FROM Accounts
        WHERE registration_time BETWEEN ? AND ?
    """, (fixed_start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date_7_days.strftime('%Y-%m-%d %H:%M:%S')))
    registrations_7_days = cursor.fetchall()

    dates_7_days = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f').date() for row in registrations_7_days]
    date_count_7_days = Counter(dates_7_days)

    # Подсчет максимального и минимального дней
    if date_count_7_days:
        max_reg_day_7 = max(date_count_7_days, key=date_count_7_days.get)
        max_reg_count_7 = date_count_7_days[max_reg_day_7]
        total_reg_7 = sum(date_count_7_days.values())

        # Изменение: расчет процентов на основе общего количества регистраций
        daily_percent_7 = {date: (count / total_reg_7) * 100 for date, count in date_count_7_days.items()}
        highest_percent_day_7 = max(daily_percent_7, key=daily_percent_7.get)
        lowest_percent_day_7 = min(daily_percent_7, key=daily_percent_7.get)

        # Запись в файл reg_for7_days.txt
        with open(f'{stat_path}reg_for7_days.txt', 'w') as f:
            f.write(f'Количество пользователей, зарегистрировавшихся за 7 дней: {total_reg_7}\n')
            f.write(f'День с наибольшим количеством регистраций: {max_reg_day_7} ({max_reg_count_7} регистраций)\n')
            f.write(
                f'Самый высокий процент регистрации: {daily_percent_7[highest_percent_day_7]:.2f}% ({highest_percent_day_7})\n')
            f.write(
                f'Самый низкий процент регистрации: {daily_percent_7[lowest_percent_day_7]:.2f}% ({lowest_percent_day_7})\n')

    # Получение регистраций за 31 день
    end_date_31_days = fixed_start_date + timedelta(days=31)
    cursor.execute("""
        SELECT registration_time FROM Accounts
        WHERE registration_time BETWEEN ? AND ?
    """, (fixed_start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date_31_days.strftime('%Y-%m-%d %H:%M:%S')))
    registrations_31_days = cursor.fetchall()

    dates_31_days = [datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f').date() for row in registrations_31_days]
    date_count_31_days = Counter(dates_31_days)

    # Подсчет максимального и минимального дней
    if date_count_31_days:
        max_reg_day_31 = max(date_count_31_days, key=date_count_31_days.get)
        max_reg_count_31 = date_count_31_days[max_reg_day_31]
        total_reg_31 = sum(date_count_31_days.values())

        # Изменение: расчет процентов на основе общего количества регистраций
        daily_percent_31 = {date: (count / total_reg_31) * 100 for date, count in date_count_31_days.items()}
        highest_percent_day_31 = max(daily_percent_31, key=daily_percent_31.get)
        lowest_percent_day_31 = min(daily_percent_31, key=daily_percent_31.get)

        # Запись в файл reg_for31_days.txt
        with open(f'{stat_path}reg_for31_days.txt', 'w') as f:
            f.write(f'Количество пользователей, зарегистрировавшихся за 31 день: {total_reg_31}\n')
            f.write(f'День с наибольшим количеством регистраций: {max_reg_day_31} ({max_reg_count_31} регистраций)\n')
            f.write(
                f'Самый высокий процент регистрации: {daily_percent_31[highest_percent_day_31]:.2f}% ({highest_percent_day_31})\n')
            f.write(
                f'Самый низкий процент регистрации: {daily_percent_31[lowest_percent_day_31]:.2f}% ({lowest_percent_day_31})\n')

    conn.close()

