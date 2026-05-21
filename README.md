# Развёртывание FastAPI + Frontend в Docker

Данный проект представляет собой ML-сервис прогнозирования уровня цифровой подростковой девиации на основе цифровых факторов риска.
Система включает backend на FastAPI, frontend-анкетирование и модель машинного обучения, упакованные в Docker-контейнеры.

## Требования

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Развёртывание

1. **Клонируйте репозиторий**
```bash
  git clone https://github.com/Prushka147/digital-deviation-forecast.git
cd digital-deviation-forecast
```
2. **Соберите и запустите контейнеры**

```bash
   docker compose up --build
```
После запуска:

Backend / Swagger

Swagger документация FastAPI будет доступна по адресу: http://localhost:8000/docs

Frontend — по адресу: http://localhost:3000  
3. **Остановка приложения**
Для остановки и удаления контейнеров, сетей и volume'ов:

docker compose down -v
```
Пример запуска
docker compose up --build
