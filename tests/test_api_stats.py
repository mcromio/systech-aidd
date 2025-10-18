"""Интеграционные тесты для Stats API."""

from fastapi.testclient import TestClient

from src.api_main import app

# Создание test client
client = TestClient(app)


class TestHealthEndpoint:
    """Тесты для health check endpoint."""

    def test_health_returns_200(self) -> None:
        """Тест: health endpoint возвращает 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self) -> None:
        """Тест: health endpoint возвращает status='ok'."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"


class TestStatsEndpoint:
    """Тесты для stats endpoint."""

    def test_stats_without_period_defaults_to_day(self) -> None:
        """Тест: без параметра period по умолчанию используется day."""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["period"] == "day"

    def test_stats_day_returns_200(self) -> None:
        """Тест: stats с period=day возвращает 200 OK."""
        response = client.get("/api/v1/stats?period=day")
        assert response.status_code == 200

    def test_stats_week_returns_200(self) -> None:
        """Тест: stats с period=week возвращает 200 OK."""
        response = client.get("/api/v1/stats?period=week")
        assert response.status_code == 200

    def test_stats_month_returns_200(self) -> None:
        """Тест: stats с period=month возвращает 200 OK."""
        response = client.get("/api/v1/stats?period=month")
        assert response.status_code == 200

    def test_stats_invalid_period_returns_400(self) -> None:
        """Тест: невалидный period возвращает 400 Bad Request."""
        response = client.get("/api/v1/stats?period=invalid")
        assert response.status_code == 422  # FastAPI валидация возвращает 422

    def test_stats_response_has_required_fields(self) -> None:
        """Тест: ответ содержит все обязательные поля."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()

        # Проверка корневых полей
        assert "period" in data
        assert "generated_at" in data
        assert "general_stats" in data
        assert "activity_chart" in data
        assert "recent_dialogs" in data
        assert "top_users" in data

    def test_stats_general_stats_structure(self) -> None:
        """Тест: general_stats имеет правильную структуру."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()
        general_stats = data["general_stats"]

        assert "total_dialogs" in general_stats
        assert "total_dialogs_change" in general_stats
        assert "active_users" in general_stats
        assert "active_users_change" in general_stats
        assert "total_messages" in general_stats
        assert "total_messages_change" in general_stats
        assert "avg_dialog_length" in general_stats
        assert "avg_dialog_length_change" in general_stats

    def test_stats_activity_chart_is_list(self) -> None:
        """Тест: activity_chart это список."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()

        assert isinstance(data["activity_chart"], list)
        assert len(data["activity_chart"]) > 0

    def test_stats_activity_chart_day_has_24_points(self) -> None:
        """Тест: activity_chart для day содержит 24 точки."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()

        assert len(data["activity_chart"]) == 24

    def test_stats_activity_chart_week_has_7_points(self) -> None:
        """Тест: activity_chart для week содержит 7 точек."""
        response = client.get("/api/v1/stats?period=week")
        data = response.json()

        assert len(data["activity_chart"]) == 7

    def test_stats_activity_chart_month_has_30_points(self) -> None:
        """Тест: activity_chart для month содержит 30 точек."""
        response = client.get("/api/v1/stats?period=month")
        data = response.json()

        assert len(data["activity_chart"]) == 30

    def test_stats_recent_dialogs_max_10_items(self) -> None:
        """Тест: recent_dialogs содержит максимум 10 элементов."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()

        assert len(data["recent_dialogs"]) <= 10

    def test_stats_recent_dialog_structure(self) -> None:
        """Тест: элементы recent_dialogs имеют правильную структуру."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()

        if data["recent_dialogs"]:
            dialog = data["recent_dialogs"][0]
            assert "user_display" in dialog
            assert "message_count" in dialog
            assert "last_active" in dialog
            assert "status" in dialog
            assert dialog["status"] in ["active", "idle", "inactive"]

    def test_stats_top_users_max_5_items(self) -> None:
        """Тест: top_users содержит максимум 5 элементов."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()

        assert len(data["top_users"]) <= 5

    def test_stats_top_user_structure(self) -> None:
        """Тест: элементы top_users имеют правильную структуру."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()

        if data["top_users"]:
            user = data["top_users"][0]
            assert "user_display" in user
            assert "message_count" in user
            assert "percentage" in user

    def test_stats_top_user_first_has_100_percent(self) -> None:
        """Тест: первый пользователь в топе имеет 100%."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()

        if data["top_users"]:
            assert data["top_users"][0]["percentage"] == 100.0

    def test_stats_different_periods_produce_different_data(self) -> None:
        """Тест: разные периоды возвращают разные данные."""
        response_day = client.get("/api/v1/stats?period=day")
        response_week = client.get("/api/v1/stats?period=week")

        data_day = response_day.json()
        data_week = response_week.json()

        # Проверяем что period различается
        assert data_day["period"] == "day"
        assert data_week["period"] == "week"

        # Проверяем что размер activity_chart разный
        assert len(data_day["activity_chart"]) != len(data_week["activity_chart"])

    def test_stats_response_is_json(self) -> None:
        """Тест: ответ в формате JSON."""
        response = client.get("/api/v1/stats?period=day")
        assert response.headers["content-type"] == "application/json"

    def test_stats_generated_at_is_iso_timestamp(self) -> None:
        """Тест: generated_at это валидный ISO timestamp."""
        response = client.get("/api/v1/stats?period=day")
        data = response.json()

        # Проверяем что это строка и содержит дату
        assert isinstance(data["generated_at"], str)
        assert "T" in data["generated_at"]  # ISO формат содержит T
        assert "Z" in data["generated_at"]  # UTC timezone


class TestOpenAPIDocumentation:
    """Тесты для OpenAPI документации."""

    def test_openapi_json_is_accessible(self) -> None:
        """Тест: OpenAPI JSON доступен."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_openapi_has_stats_endpoint(self) -> None:
        """Тест: OpenAPI документация содержит stats endpoint."""
        response = client.get("/openapi.json")
        openapi_spec = response.json()

        # Проверяем наличие endpoint /api/v1/stats
        assert "/api/v1/stats" in openapi_spec["paths"]

    def test_swagger_docs_page_accessible(self) -> None:
        """Тест: Swagger UI страница доступна."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    def test_redoc_page_accessible(self) -> None:
        """Тест: ReDoc страница доступна."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "redoc" in response.text.lower() or "api" in response.text.lower()
