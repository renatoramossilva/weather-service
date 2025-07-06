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
