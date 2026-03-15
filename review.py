import os, requests

import requests, sys, json

try:
    with open("pr_diff.txt", "r") as f:
        diff = f.read()

    if not diff.strip():
        print("No diff found, skipping.")
        sys.exit(0)

    prompt = f"""You are a senior code reviewer. Review this git diff and provide:
    1. Potential bugs
    2. Code quality issues
    3. Suggestions for improvement

    Make sure to indicate the offending lines.

    Diff:
    {diff}
    """

    response = requests.post(
        "http://localhost:8000/generate",
        json={"prompt": f"{prompt}", "model": "qwen2.5-coder:7b"},
        timeout=999
    )
    response.raise_for_status()
    review = response.json()["response"]
    print(review)

except FileNotFoundError:
    print("❌ pr_diff.txt not found")
    sys.exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to FastAPI at localhost:8000 — is it running?")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

gh_token = os.environ["GITHUB_TOKEN"]
repo = os.environ["GITHUB_REPOSITORY"]
pr_number = os.environ["PR_NUMBER"]

requests.post(
    f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
    headers={"Authorization": f"Bearer {gh_token}"},
    json={"body": f"## Here's what the PR Police says:\n\n{review}"}
)
