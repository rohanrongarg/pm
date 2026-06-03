from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import Cookie, Depends, FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.ai import ping_openrouter, run_structured_chat
from app.db import (
    create_session,
    delete_session,
    get_or_create_board,
    get_user_by_username,
    get_user_for_session,
    init_db,
    save_board,
)
from app.schemas import BoardData, ChatRequest, ChatResponse, LoginRequest, SessionResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="PM MVP Backend", lifespan=lifespan)
frontend_dist = Path(__file__).resolve().parents[2] / "frontend-dist"
SESSION_COOKIE_NAME = "pm_session"

SCAFFOLD_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PM MVP Scaffold</title>
    <style>
      body {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f7f8fb;
        color: #032147;
      }
      main {
        max-width: 800px;
        margin: 56px auto;
        padding: 24px;
      }
      h1 {
        margin: 0 0 8px 0;
      }
      p {
        color: #666;
      }
      button {
        border: 0;
        border-radius: 999px;
        padding: 10px 18px;
        background: #753991;
        color: white;
        cursor: pointer;
      }
      pre {
        margin-top: 18px;
        padding: 14px;
        border-radius: 12px;
        background: white;
        border: 1px solid rgba(3, 33, 71, 0.12);
      }
    </style>
  </head>
  <body>
    <main>
      <h1>PM MVP backend scaffold is running</h1>
      <p>This page is served by FastAPI. Use the button to call <code>/api/hello</code>.</p>
      <button id="call-api" type="button">Call hello API</button>
      <pre id="result">Waiting for API call...</pre>
    </main>
    <script>
      const button = document.getElementById("call-api");
      const result = document.getElementById("result");
      button?.addEventListener("click", async () => {
        result.textContent = "Calling /api/hello...";
        try {
          const response = await fetch("/api/hello");
          const payload = await response.json();
          result.textContent = JSON.stringify(payload, null, 2);
        } catch (error) {
          result.textContent = `Request failed: ${String(error)}`;
        }
      });
    </script>
  </body>
</html>
"""


def current_user(session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> dict:
    if not session_token:
        raise HTTPException(status_code=401, detail="Authentication required.")
    user = get_user_for_session(session_token)
    if not user:
        raise HTTPException(status_code=401, detail="Session is invalid.")
    return user


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/hello")
async def hello() -> dict[str, str]:
    return {"message": "Hello from FastAPI in Docker"}


@app.post("/api/auth/login", response_model=SessionResponse)
async def login(payload: LoginRequest, response: Response) -> SessionResponse:
    user = get_user_by_username(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_session(user["id"])
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
    )
    return SessionResponse(authenticated=True, username=user["username"])


@app.post("/api/auth/logout")
async def logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> dict[str, bool]:
    if session_token:
        delete_session(session_token)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"success": True}


@app.get("/api/auth/session", response_model=SessionResponse)
async def session(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> SessionResponse:
    if not session_token:
        return SessionResponse(authenticated=False)
    user = get_user_for_session(session_token)
    if not user:
        return SessionResponse(authenticated=False)
    return SessionResponse(authenticated=True, username=user["username"])


@app.get("/api/board", response_model=BoardData)
async def get_board(user: dict = Depends(current_user)) -> BoardData:
    return get_or_create_board(user["id"])


@app.put("/api/board", response_model=BoardData)
async def put_board(payload: BoardData, user: dict = Depends(current_user)) -> BoardData:
    return save_board(user["id"], payload)


@app.post("/api/ai/ping")
async def ai_ping(user: dict = Depends(current_user)) -> dict[str, str]:
    del user
    content = await ping_openrouter()
    return {"result": content}


@app.post("/api/ai/chat", response_model=ChatResponse)
async def ai_chat(payload: ChatRequest, user: dict = Depends(current_user)) -> ChatResponse:
    message, next_board = await run_structured_chat(payload)
    persisted = save_board(user["id"], next_board)
    return ChatResponse(message=message, board=persisted)


@app.get("/scaffold", response_class=HTMLResponse)
async def scaffold() -> str:
    return SCAFFOLD_HTML


if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return SCAFFOLD_HTML
