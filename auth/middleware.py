from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from auth.jwthandler import decode_access_token
from models.users import User as user_models
from core.database import SessionLocal
from fastapi.responses import RedirectResponse


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        print(path)
        # Skip auth for login, signup, and docs
        public_paths = ["/users/login", "/users/signup", "/docs", "/openapi.json", "/static"]
        if any(path.startswith(p) for p in public_paths):
            return await call_next(request)

        token = request.cookies.get("access_token")
        user_id = None

        if token:
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("sub")

        # Attach user_id to request.state (even if it's None)
        request.state.user_id = user_id

        # OPTIONAL: redirect to login if user_id is required for HTML pages
        if not user_id:
            return RedirectResponse(url="/login")

        return await call_next(request)
