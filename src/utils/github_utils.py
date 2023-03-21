import requests
import json

from src.config import Config


def create_issue(user_name_from_report: str, body: str) -> dict:
    title = f"Issue from {user_name_from_report}'s report"
    headers = {"Authorization": f"token {Config.GITHUB_TOKEN}"}
    data = {"title": title, "body": body, 'assignees': [Config.DEVELOPER_GH_PROFILE]}
    url = f"https://api.github.com/repos/{Config.DEVELOPER_GH_PROFILE}/{Config.BOT_GH_REPO}/issues"

    response = requests.post(url, data=json.dumps(data), headers=headers)

    code = response.status_code
    resp_dict = {'code': code}

    if code == 201:
        resp = response.json()
        issue_url = resp['html_url']
        developer_text = f"✅ [Issue]({issue_url}) створено успішно!"

        resp_dict |= {'url': issue_url}
    else:
        developer_text = f'❌ Не вдалось створити issue. Status code: {response.status_code}'

    resp_dict |= {'developer_text': developer_text, }

    return resp_dict
