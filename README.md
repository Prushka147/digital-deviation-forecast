Развёртывание FastAPI + React в Docker
Этот шаблон представляет собой базовую настройку веб-приложения с использованием FastAPI (backend) и React (frontend), упакованных в контейнеры Docker.

Требования
Docker
Docker Compose
Развёртывание
Клонируйте репозиторий
   git clone https://github.com/denismilyukov/teenage-deviation-predicting
   cd teenage-deviation-predicting
Соберите и запустите контейнеры
   docker-compose up --build
После запуска:

Backend будет доступен по адресу: http://localhost

Frontend — по адресу: http://localhost:3000
3. Остановка приложения Для остановки и удаления контейнеров, сетей и volume'ов:

docker-compose down -v
"# FastAPI-React-Docker-Template"
