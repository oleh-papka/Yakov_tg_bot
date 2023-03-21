import requests
import json

from src.config import Config


def create_issue(user_name_from_report: str, body: str) -> str:
    title = f"Issue from {user_name_from_report}'s report"
    headers = {"Authorization": f"token {Config.GITHUB_TOKEN}"}
    data = {"title": title, "body": body, 'assignees': [Config.DEVELOPER_GH_PROFILE]}
    url = f"https://api.github.com/repos/{Config.DEVELOPER_GH_PROFILE}/{Config.BOT_GH_REPO}/issues"

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 201:
        resp = response.json()
        resp_text = f"✅ [Issue]({resp['html_url']}) створено успішно!"
    else:
        resp_text = f'❌ Не вдалось створити issue. Status code: {response.status_code}'

    return resp_text
