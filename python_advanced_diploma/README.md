# Сервис микроблогов (Twitter-like)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-brightgreen.svg)](https://postgresql.org)

Бэкенд-сервис для корпоративного микроблогинга с API на FastAPI и PostgreSQL.

## 📌 Возможности

- Создание/удаление твитов (до 280 символов)
- Лайки и репосты
- Подписки на пользователей
- Загрузка медиафайлов
- Лента с сортировкой по популярности
- JWT-аутентификация через API-ключи

## 🚀 Быстрый старт

### Предварительные требования
- Docker 20.10+
- Docker Compose 1.29+

### Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/microblog-backend.git
   cd microblog-backend