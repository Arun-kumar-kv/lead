import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "property_db")

    # Laravel Sanctum integration
    LARAVEL_BASE_URL = os.getenv("LARAVEL_BASE_URL", "https://host.trandad.ae:8000")
    LARAVEL_LOGIN_ENDPOINT = os.getenv("LARAVEL_LOGIN_ENDPOINT", "/api/v1/admin/login-new")
    # Must point to an authenticated "current user" endpoint in Laravel
    LARAVEL_ME_ENDPOINT = os.getenv("LARAVEL_ME_ENDPOINT", "/api/v1/admin/me")
    LARAVEL_TIMEOUT_SECONDS = int(os.getenv("LARAVEL_TIMEOUT_SECONDS", "15"))

settings = Settings()