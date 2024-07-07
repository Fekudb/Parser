import asyncio
import logging
import os
import requests
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
import psycopg2

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
}

# Функция создания таблицы db если ее нет
def create_table():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            company VARCHAR(255),
            title VARCHAR(255),
            salary VARCHAR(255),
            skills TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Функция занесения данных в таблицу db 
def insert_vacancy(company, title, salary, skills):
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vacancies (company, title, salary, skills) VALUES (%s, %s, %s, %s)
    """, (company, title, salary, skills))
    conn.commit()
    cursor.close()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Добро пожаловать! Пожалуйста, введите Ваш запрос для поиска вакансий.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text
    await update.message.reply_text(f'Вы ввели запрос: {query}. Начинаем парсинг вакансий...')
    await parse_vacancies(update, context, query)

async def parse_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str) -> None:
    url = f'https://career.habr.com/vacancies?q={query}'  # передача запроса на париснг 
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        vacancies = soup.find_all('div', class_='vacancy-card__info')[:5]

        if not vacancies:
            await update.message.reply_text("К сожалению не удалось найти вакансии по Вашему запросу(")
            return

        for vacancy in vacancies:
            company = vacancy.find('div', class_='vacancy-card__company-title').text.strip()
            title = vacancy.find('div', class_='vacancy-card__title').text.strip()
            salary = vacancy.find('div', class_='vacancy-card__salary').text.strip() if vacancy.find('div', class_='vacancy-card__salary') else 'Не указана'
            skills = ', '.join([skill.text for skill in vacancy.find_all('a', class_='link-comp')])

            # Вывод данных парсинга пользователю 
            insert_vacancy(company, title, salary, skills)

            await update.message.reply_text(f"Вакансия: {title}\nКомпания: {company}\nЗарплата: {salary}\nНавыки: {skills}")
    else:
        await update.message.reply_text("Не удалось получить данные с сайта.")

def main() -> None:
    
    create_table()

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
