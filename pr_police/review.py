import os, requests, sys

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
    prompt = f"""You are a senior code reviewer. Review this git diff and assess:
    1. PEP-8 Compliance
    2. Possible bugs
    3. Possible security considerations
    4. Suggestions for improvement with fully rewritten code

    At the top of your answer, include a verdict wherein if there are any obvious issues, say CODE IS REJECTED.
    Otherwise, say CODE IS ACCEPTED.

    Diff:
    {diff}
    """

    response = requests.post(
        "http://localhost:8000/generate",
        json={"prompt": prompt, "model": "qwen2.5-coder:7b"},
        timeout=999
    )
    response.raise_for_status()
    review = response.json()["response"]
    print(review)

except requests.exceptions.ConnectionError:
    print("❌ Could not connect to FastAPI at localhost:8000 — is it running?")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error getting review: {e}")
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

if "CODE IS REJECTED" in review.upper():
    print("This code has been rejected")
    sys.exit(1)
elif "CODE IS ACCEPTED":
    print("This code has been conditionally accepted")
    sys.exit(0)
