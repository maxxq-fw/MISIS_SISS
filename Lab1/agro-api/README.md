# Agro Scoring API

Сервис принимает данные о сельскохозяйственном предприятии и рассчитывает уровень риска.

## Что есть в проекте

- `GET /health` — проверка, что API работает;
- `GET /model-info` — информация о модели;
- `POST /predict` — расчет риска;
- `GET /predictions/{request_id}` — получение результата по ID;
- `GET /predictions` — список сохраненных результатов.

## Запуск

Перейти в папку `agro-api` и создать виртуальное окружение:

```bash
python -m venv venv
```

Для Windows активировать его командой:

```bash
venv\Scripts\activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

Запустить сервер:

```bash
uvicorn main:app --reload
```

После запуска Swagger будет доступен здесь:

```text
http://127.0.0.1:8000/docs
```

Проверка состояния API:

```text
http://127.0.0.1:8000/health
```

## Пример запроса

Для `POST /predict` можно использовать такие данные:

```json
{
  "farm_id": "FARM-001",
  "region": "Krasnodar",
  "crop_type": "wheat",
  "area_ha": 2500,
  "temperature_avg": 24.3,
  "precipitation_mm": 320,
  "payment_delay_days": 45,
  "previous_defaults": 1,
  "debt": 6500000
}
```

Допустимые регионы: `Krasnodar`, `Rostov`, `Stavropol`.
