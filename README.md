# 🌤️ Weather Service API

[![CI](https://github.com/renatoramossilva/weather-service/actions/workflows/check.yaml/badge.svg)](https://github.com/renatoramossilva/weather-service/actions/workflows/check.yaml)

A simple and modern FastAPI project that provides current weather information for a given city using the [WeatherAPI](https://www.weatherapi.com/).


## 📁 Project Structure

```sh
├── app
│   ├── api
│   │   └── v1
│   │       ├── routes.py
│   │       └── schemas.py
│   ├── main.py
│   └── services
│       └── weather_services.py
├── pyproject.toml
└── uv.lock
```

## 🚀 How to Run the App

### 1. 📦 Install Dependencies

Using [`uv`](https://github.com/astral-sh/uv) (recommended):

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 2. 🔐 Set Your API Key
Create a .env file in the root folder with your WeatherAPI key:

```sh
WEATHER_API_KEY=<your_api_key_here>
```

Your key can be obtained for free at: https://www.weatherapi.com/


### 3. 🏁 Start the Server

```sh
uv uvicorn app.main:app --reload
```

Server will run at: http://127.0.0.1:8000

📚 API Documentation
Once the app is running, you can explore the API using the interactive Swagger UI:

👉 http://localhost:8000/docs – Interactive documentation powered by FastAPI & Swagger UI

🔎 Available Endpoint
```sh
GET /api/v1/weather/{city}
```

Returns current weather data for the specified city.

✅ Example:

```sh
curl -s http://127.0.0.1:8000/api/v1/weather/barcelona | jq

{
  "city": "Barcelona",
  "country": "Spain",
  "temperature_celsius": 27.5,
  "condition": "Partly cloudy",
  "local_time": "2025-07-06T18:42:00"
}
```


## ✅ CI: Linters & Branch Protection

This project includes a **GitHub Actions pipeline** that runs automatic code quality checks on every Pull Request targeting the `master` branch:

- ✅ **Black** – Python code formatter
- ✅ **Ruff** – Linter and style checker
- ✅ **Mypy** – Static type checker

🔒 **Merges to `master` are only allowed if all checks pass.**

This ensures high code quality and consistency across the project.


## 🐳 Docker Compose Support

You can use docker-compose to run the app in a containerized development environment:

```
docker-compose up --build
```

This will:

- Build the image using the provided Dockerfile

- Start the FastAPI application at http://localhost:8000


## ⚡ Redis Cache Support


This project supports response caching via Redis to improve performance and reduce external API calls.

### 🧠 How It Works


When a request is made to the weather endpoint:

The API first checks if the data for the given city is already cached in Redis.

If cached, it returns the stored result.

If not, it fetches fresh data from the WeatherAPI, stores it in Redis (30 min), and returns the result.

This approach significantly reduces latency and external API usage.



### 🌐 Access RedisInsight


For easy monitoring and management of the Redis instance, it is possible to use RedisInsight — a powerful GUI tool.

Open your browser and go to:

http://localhost:8001/

Here, you can visualize your Redis keys, monitor performance, and manage the cache in a friendly interface.
