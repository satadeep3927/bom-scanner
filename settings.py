from os import getenv

LLM_API_KEY = getenv("LLM_API_KEY", "")
LLM_API_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"
LLM_MODEL = "gemini-2.5-flash"
