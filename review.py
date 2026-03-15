import os, requests

with open("pr_diff.txt", "r") as f:
    diff = f.read()

prompt = f"""You are a senior code reviewer. Review this git diff and provide:
1. Potential bugs
2. Code quality issues
3. Suggestions for improvement

Diff:
{diff}
"""

response = requests.post(
    "http://localhost:8000/generate",
    json={"prompt": prompt, "model": "qwen2.5-coder:7b"}
)

review = response.json()["response"]

# Fail the action if serious issues found (optional)
if "critical" in review.lower() or "bug" in review.lower():
    exit(1)

gh_token = os.environ["GITHUB_TOKEN"]
repo = os.environ["GITHUB_REPOSITORY"]
pr_number = os.environ["PR_NUMBER"]

requests.post(
    f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
    headers={"Authorization": f"Bearer {gh_token}"},
    json={"body": f"## Here's what the PR Police says:\n\n{review}"}
)
