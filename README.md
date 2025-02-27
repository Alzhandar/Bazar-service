# Bazar-service 🛍️

<div align="center">
  <img src="docs/images/logo.png" alt="Bazar-service Logo" width="200"/>
  
  [![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
  [![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
</div>

## 🌐 Демо
- Живая версия: [Bazar-service](https://dolphin-app-zscjm.ondigitalocean.app/)

<div align="center">
  <img src="docs/images/preview.png" alt="Bazar-service Preview" width="800"/>
</div>

## 📝 Описание проекта
Bazar-service - современная платформа электронной коммерции, предоставляющая пользователям возможность легко покупать и продавать товары. Наше приложение сочетает в себе интуитивно понятный интерфейс с мощной функциональностью для эффективного ведения онлайн-торговли.

## ✨ Основные возможности

### 👥 Для пользователей
- Регистрация и авторизация через email/пароль или социальные сети
- Личный кабинет с историей заказов и избранными товарами
- Корзина покупок с сохранением между сессиями

<div align="center">
  <img src="meadia/readme/user_list.png" alt="User Features" width="600"/>
  <img src="meadia/readme/about_product.png" alt="User Features" width="600"/>
</div>

### 🏪 Для продавцов
- Управление каталогом товаров
- Аналитика продаж и статистика
- Обработка заказов и управление статусами
- Система уведомлений о новых заказах

<div align="center">
  <img src="meadia/readme/create_product.png" alt="Seller Features" width="600"/>
  <img src="meadia/readme/orders_list.png" alt="Seller Features" width="600"/>
  <img src="meadia/readme/product_list.png" alt="Seller Features" width="600"/>

</div>

## 🛠 Технологический стек

### Backend
- **Framework**: Django 4.2
- **API**: Django REST Framework
- **База данных**: PostgreSQL
- **Кеширование**: Redis
- **Очереди**: Celery
- **Поиск**: Elasticsearch

### Frontend
- **Шаблонизация**: Django Templates
- **Стили**: SCSS
- **JavaScript**: ES6+
- **Сборка**: Webpack

### Инфраструктура
- **Контейнеризация**: Docker
- **CI/CD**: GitHub Actions
- **Хостинг**: DigitalOcean
- **Хранение файлов**: AWS S3
- **Мониторинг**: Sentry

## 🚀 Установка и запуск

### Предварительные требования
- Python 3.9+
- PostgreSQL 13+
- Redis
- Node.js 14+

### Локальная установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/Alzhandar/Bazar-service.git
cd Bazar-service
```

2. Создать виртуальное окружение и установить зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate  # для Windows
pip install -r requirements.txt
```

3. Настроить переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл, добавив необходимые значения
```

4. Применить миграции и создать суперпользователя:
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Запустить проект:
```bash
python manage.py runserver
```

### Docker установка

```bash
docker-compose up -d
```

## 📊 Скриншоты

<div align="center">
  <img src="docs/images/screenshot-1.png" alt="Dashboard" width="400"/>
  <img src="docs/images/screenshot-2.png" alt="Product List" width="400"/>
  <img src="docs/images/screenshot-3.png" alt="Order Details" width="400"/>
  <img src="docs/images/screenshot-4.png" alt="Analytics" width="400"/>
</div>

## 📈 Архитектура проекта

<div align="center">
  <img src="docs/images/architecture.png" alt="Project Architecture" width="800"/>
</div>

## 🤝 Вклад в проект
Мы приветствуем вклад в развитие проекта! Пожалуйста, ознакомьтесь с нашим руководством по содействию.

## 📝 Лицензия
Проект распространяется под лицензией MIT. Подробности в файле LICENSE.

## 👤 Автор
- **Alzhandar**
  - GitHub: [@Alzhandar](https://github.com/Alzhandar)
  - Email: [alzhandar@example.com](mailto:alzhandar@example.com)

## 🙏 Благодарности
- Всем контрибьюторам проекта
- Сообществу Django
- Нашим пользователям за отзывы и предложения

<div align="center">
  <sub>Built with ❤️ by Alzhandar</sub>
</div>