import os
import requests

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO_OWNER = 'osherboudara99'
REPO_NAME = 'My_Resume_WebApp'
BRANCH = 'main'
COMMIT_MESSAGE = "Scheduled prevent sleep mode commit from Lambda"

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def get_latest_commit_sha():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/ref/heads/{BRANCH}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['object']['sha']

def get_tree_sha(commit_sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits/{commit_sha}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['tree']['sha']

def create_commit(tree_sha, parent_sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/commits"
    data = {
        "message": COMMIT_MESSAGE,
        "tree": tree_sha,
        "parents": [parent_sha]
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()['sha']

def update_ref(commit_sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/{BRANCH}"
    data = {
        "sha": commit_sha
    }
    response = requests.patch(url, json=data, headers=headers)
    response.raise_for_status()

def lambda_handler(event, context):
    latest_commit_sha = get_latest_commit_sha()
    tree_sha = get_tree_sha(latest_commit_sha)
    new_commit_sha = create_commit(tree_sha, latest_commit_sha)
    update_ref(new_commit_sha)
    return {"status": "success", "commit_sha": new_commit_sha}
