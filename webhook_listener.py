# webhook_listener.py

from flask import Flask, request, jsonify
import requests
import hmac
import hashlib
import os

app = Flask(__name__)

GITHUB_SECRET = os.environ.get('GITHUB_SECRET')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = 'nickchase'
REPO_NAME = 'ai-assistant'

def verify_signature(data, signature):
    mac = hmac.new(bytes(GITHUB_SECRET, 'utf-8'), msg=data, digestmod=hashlib.sha256)
    return hmac.compare_digest('sha256=' + mac.hexdigest(), signature)

def create_feature_branch(issue_number, issue_title):
    # Get default branch SHA
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs/heads/main'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    sha = response.json()['object']['sha']

    # Define branch name
    branch_name = f'feature/issue-{issue_number}-{issue_title.replace(" ", "-")}'

    # Create new branch
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/refs'
    data = {'ref': f'refs/heads/{branch_name}', 'sha': sha}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f'Branch {branch_name} created successfully.')
    else:
        print(f'Failed to create branch: {response.content}')

@app.route('/', methods=['GET','POST'])
def index():
    return "HI!"

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(payload, signature):
        return jsonify({'message': 'Invalid signature'}), 400

    event = request.headers.get('X-GitHub-Event')
    print(f'Event = {event}')
    if event == 'issues':
        issue = request.json['issue']
        if request.json['action'] == 'opened':
            issue_number = issue['number']
            issue_title = issue['title']
            create_feature_branch(issue_number, issue_title)

    if event == 'pull_request':
        if request.json['action'] == 'opened':
            pull_number = request.json['pull_request']['number']
            assign_reviewers(pull_number)

    return jsonify({'message': 'Success'}), 200

def assign_reviewers(pull_number):
    # Placeholder logic for assigning reviewers
    potential_reviewers = ['roadnick', 'alice', 'bob', 'carol']
    reviewers = potential_reviewers[:1]  # Assign first two for simplicity

    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pull_number}/requested_reviewers'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {'reviewers': reviewers}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print('Reviewers assigned successfully.')
    else:
        print(f'Error assigning reviewers: {response.content}')

if __name__ == '__main__':
    app.run(port=5000)

