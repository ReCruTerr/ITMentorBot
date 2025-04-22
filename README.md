
# 🤖 IT Interview Trainer Bot

Telegram-бот для подготовки к техническим собеседованиям в сфере IT.  
Работает на **Python + Django + Aiogram 3.0**, поддерживает взаимодействие с **OpenAI**, и предлагает вопросы, проверку ответов, а также советы по улучшению.

---

## 🚀 Возможности

- ❓ Генерация вопросов по IT-направлениям (Python, SQL, системы и др.)
- 🧠 Проверка ответов с помощью LLM (OpenAI / Mistral)
- 📊 Админ-панель на Django для управления сессиями
- 🔄 Асинхронная архитектура на Aiogram 3.0
- 🗂 Хранение истории сессий и прогресса
- ⏱ Встроенная поддержка таймеров/лимитов на ответ (по желанию)

---

## 🧰 Технологии

- Python 3.10+
- Django 5.0
- Aiogram 3.19.0
- Celery + Redis
- Mistral / OpenAI API
- PostgreSQL / SQLite
- dotenv для конфигурации

---

## ⚙️ Как работает бот

1. **Выбор уровня (грейда):**  
   Junior / Middle / Senior — бот подбирает сложность вопросов в зависимости от уровня пользователя.

2. **Выбор языка программирования:**  
   Например: Python, JavaScript, Go и др.

3. **Выбор сферы:**  
   Backend, SQL, ООП, алгоритмы и структуры данных, DevOps и др.

4. **Генерация вопросов:**  
   Используется LLM (**Mistral**) для создания **5 вопросов**, соответствующих выбранным параметрам.

5. **Ответы пользователя:**  
   Пользователь последовательно отвечает на каждый вопрос. Ответы сохраняются.

6. **Анализ и обратная связь:**  
   Модель анализирует ответы, оценивает знания и даёт **вердикт + рекомендации по улучшению**.

---

## 🛠️ Установка и запуск

1. Клонируйте репозиторий:

```bash
git clone https://github.com/your-username/interview-trainer-bot.git
cd interview-trainer-bot
```

2. Установите виртуальное окружение и зависимости:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе шаблона:

```env
BOT_TOKEN=your_telegram_bot_token
MISTRAL_API_KEY=your_mistral_or_openai_key
REDIS_URL=redis://localhost:6379
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
```

4. Примените миграции и создайте суперпользователя:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Запустите и бота:
```bash
cd tgproject
python -m bot.bot
```
---

## 📁 Структура проекта

```
.
├── bot/               # Приложение Django + логика Telegram-бота (Aiogram)
│   ├── ai/            # Работа с LLM (например, Mistral, OpenAI)
│   ├── migrations/    # Миграции Django
│   ├── scripts/       # Скрипты и инициализация
│   ├── templates/     # HTML-шаблоны Django
│   ├── admin.py       # Админ-панель Django
│   ├── apps.py        # Конфигурация приложения
│   ├── bot.py         # Точка входа Telegram-бота
│   ├── handlers.py    # Обработчики сообщений Aiogram
│   ├── keyboards.py   # Telegram-клавиатуры
│   ├── models.py      # Модели базы данных
│   ├── states.py      # Состояния FSM Aiogram
│   ├── urls.py        # URL-маршруты Django
│   ├── views.py       # Представления Django
│   └── tests.py       # Юнит-тесты
├── tgproject/         # Конфигурация всего Django-проекта
├── manage.py          # Утилита управления Django
├── db.sqlite3         # Локальная база данных SQLite
├── .env               # Переменные окружения (в .gitignore)
├── .env.example       # Пример конфигурации .env
└── venv/              # Виртуальное окружение (в .gitignore)

```

---

## 📌 Планы на развитие

- [ ] Расширение количества языков и сфер
- [ ] Настройка уровней сложности вручную
- [ ] Тематическая статистика пользователя
- [ ] Экспорт отчётов в PDF

---

## 🧪 Тестирование

Для запуска тестов:

```bash
pytest
```

---

## 👤 Автор

Разработано с вниманием к деталям и желанием помочь другим прокачать свои навыки перед IT-собеседованиями.  
**Автор:** Ренат — [Telegram](https://t.me/ARV_15)  
