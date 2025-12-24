from typing import Dict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_API_BASE: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    LLM_MODEL: str = "gemini-2.5-flash"
    GITHUB_COPILOT_TOKEN: str = ""
    EXTRA_HEADERS: Dict[str, str] | None = {
        "editor-version": "vscode/1.104.0",
        "editor-plugin-verion": "copilot.vim/1.16.0",
        "user-agent": "GithubCopilot/1.155.0",
        "Copilot-Vision-Request": "true",
    }

    model_config = {"env_file": ".env"}


settings = Settings()
