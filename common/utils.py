import requests

from common.settings import settings


def get_access_token_from_copilot() -> str:
    """
    Retrieves the access token for Copilot from Github API.

    Returns:
        str: The access token if found, otherwise an empty string.
    """

    response = requests.get(
        "https://api.github.com/copilot_internal/v2/token",
        headers={
            "authorization": f"token {settings.GITHUB_COPILOT_TOKEN}",
            "editor-version": "Neovim/0.6.1",
            "editor-plugin-verion": "copilot.vim/1.16.0",
            "user-agent": "GithubCopilot/1.155.0",
        },
        timeout=10,
    )
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch access token: {response.status_code} - {response.text}"
        )
    payload = response.json()
    token = payload.get("token", "")
    return token
