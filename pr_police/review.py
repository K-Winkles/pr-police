import os
import requests
import sys

# --- Get diff ---
try:
    with open("pr_police/pr_diff.txt", "r") as f:
        diff = f.read()

    if not diff.strip():
        print("No diff found, skipping.")
        sys.exit(0)

except FileNotFoundError:
    print("❌ pr_diff.txt not found")
    sys.exit(1)

# --- Get review from Ollama ---
try:
    pr_review_url = os.getenv('PR_REVIEW_URL')
    model = os.getenv('MODEL')

    if not pr_review_url:
        raise ValueError("PR_REVIEW_URL environment variable is not set")

    data = {'prompt': f"""You are a senior code reviewer. Review this git diff and assess:
        1. PEP-8 Compliance
        2. Possible bugs
        3. Possible security considerations

        At the top of your answer, include a verdict wherein if there are any major security issues, say CODE IS REJECTED.
        Otherwise, say CODE IS ACCEPTED.
            
        Include a summary rating the above 4 criteria out of 5 stars.
            
        Your tone should be conversational, as if you're a cool older guy mentoring a younger junior developer.
            
        Make a joke about how old you are.

        Diff:
        {diff}""",
        "model": model
    }

    response = requests.post(pr_review_url, json=data, timeout=999)
    response.raise_for_status()
    review = response.json().get['response']
    if not review:
        raise ValueError("No review received from the server")

except (requests.RequestException, KeyError, ValueError) as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# --- Post to PR ---
try:
    print("Now posting to the PR thread...")

    gh_token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]

    result = requests.post(
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
        headers={
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json"
        },
        json={"body": f"## 🚔 PR Police Report\n\n{review}"}
    )

    print(f"GitHub API status: {result.status_code}")
    if result.status_code == 201:
        print("✅ Posted to PR thread successfully")
    else:
        print(f"❌ Failed: {result.text}")
        sys.exit(1)

except KeyError as e:
    print(f"❌ Missing environment variable: {e}")
    sys.exit(1)

# --- Check if code is rejected or conditionally accepted ---

if  review.upper().contains("CODE IS REJECTED"):
    print("Code has been rejected")
    sys.exit(1)
else:
    print("Code has been accepted")
    sys.exit(0)
