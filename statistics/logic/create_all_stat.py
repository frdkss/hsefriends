import schedule
import os
import time
from age_statistic import generate_age_statistic
from reg_statistic import generate_reg_statistic, write_registration_statistics
from sex_statistic import generate_sex_statistic
from users_statistic import generate_users_statistic

db_path = os.path.abspath(r'../../database/accounts.db')
stat_path = "../statistic_png/age_stat/"

def job():
    print("Running statistics generation...")
    generate_reg_statistic(db_path, days=2)
    generate_reg_statistic(db_path, days=7)
    generate_reg_statistic(db_path, days=31)
    write_registration_statistics(db_path)
    generate_users_statistic(db_path)
    generate_sex_statistic(db_path)
    generate_age_statistic(db_path)
    print("Statistics generation completed.")

# Запланируем выполнение задачи каждые 2 часа
schedule.every(2).hours.do(job)

# Выполним задачу сразу при запуске
job()

while True:
    schedule.run_pending()
    time.sleep(1)
