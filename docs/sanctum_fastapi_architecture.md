# Laravel Sanctum + React + FastAPI Architecture

## Request Flow

1. **React** calls Laravel login endpoint:
   - `POST /api/v1/admin/login-new`
   - body: `{ "username": "lease_admin", "password": "123" }`
2. **Laravel** returns Sanctum token.
3. **React** stores token (HTTP-only cookie preferred; localStorage possible if needed).
4. **React** calls FastAPI business endpoints with:
   - `Authorization: Bearer <sanctum_token>`
5. **FastAPI** uses auth dependency to validate the token against Laravel `/me`.
6. **Laravel** confirms token and returns current admin.
7. **FastAPI** processes business logic with authenticated admin context.

## FastAPI Layers

- **Router Layer** (`app/api/v1/auth.py`)
  - HTTP endpoints only
  - delegates auth identity extraction to dependency
- **Dependency Layer** (`app/dependencies/auth_dependencies.py`)
  - parses `Authorization` header
  - calls auth service
  - returns normalized `AuthenticatedAdmin` context
- **Service Layer** (`app/services/laravel_auth_service.py`)
  - calls Laravel login + `/me`
  - maps Laravel/network errors to FastAPI HTTP errors
- **Schema Layer** (`app/schemas/auth_schemas.py`)
  - request/response contracts for frontend

## FastAPI Auth Endpoints

- `POST /api/v1/auth/login`
  - Input:
    ```json
    { "username": "lease_admin", "password": "123" }
    ```
  - Output: Laravel login response including Sanctum token.

- `GET /api/v1/auth/me`
  - Header: `Authorization: Bearer <token>`
  - Output: `authenticated`, `user_id`, `user_email`, full user payload.

- `GET /api/v1/auth/protected-example`
  - Same token validation behavior as `/me`.
