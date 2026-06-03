import json
import os

import httpx
from fastapi import HTTPException

from app.schemas import BoardData, ChatRequest, StructuredAiResponse

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-120b"


def _extract_json(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


async def _call_openrouter(messages: list[dict[str, str]]) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY is not configured.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text or str(exc)
            raise HTTPException(
                status_code=502,
                detail=f"OpenRouter request failed: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"OpenRouter network error: {exc}",
            ) from exc

    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        raise HTTPException(status_code=502, detail="OpenRouter returned an empty response.")
    return content


async def ping_openrouter() -> str:
    content = await _call_openrouter(
        [
            {"role": "system", "content": "You are concise and accurate."},
            {"role": "user", "content": "What is 2+2? Respond with only the answer."},
        ]
    )
    return content.strip()


async def run_structured_chat(request: ChatRequest) -> tuple[str, BoardData]:
    system_prompt = (
        "You are a kanban assistant. Respond with strict JSON only and no markdown. "
        'Output schema: {"message": string, "board_update": BoardData | null}. '
        "BoardData schema: {columns: [{id,title,cardIds:string[]}], cards: "
        "{[id]: {id,title,details}}}. If no change is needed, set board_update to null."
    )

    history_lines = [f"{item.role}: {item.content}" for item in request.history]
    user_prompt = (
        "Current board JSON:\n"
        f"{request.board.model_dump_json(indent=2)}\n\n"
        "Conversation history:\n"
        f"{chr(10).join(history_lines) if history_lines else '(none)'}\n\n"
        f"User message: {request.message}"
    )

    content = await _call_openrouter(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    json_text = _extract_json(content)
    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"AI returned non-JSON output: {content}",
        ) from exc

    structured = StructuredAiResponse.model_validate(parsed)
    next_board = structured.board_update or request.board
    return structured.message, next_board
