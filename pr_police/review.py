import os
import requests
import sys
import re

def ask_model(input):
    """
    Sends request to the model
    """
    pr_review_url = os.getenv('PR_REVIEW_URL')
    model = os.getenv('MODEL')

    if not pr_review_url:
        raise ValueError("PR_REVIEW_URL environment variable is not set")
    
    data = {'prompt': input,
        "model": model
    }

    response = requests.post(pr_review_url, json=data, timeout=999)
    response.raise_for_status()
    review = response.json()['response']

    return review

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

    input = f"""You are a senior code reviewer.
    Your tone should be conversational, as if you're a cool older guy mentoring a younger junior developer.
        Make a joke about how old you are.
            
        At the top of the file: put VERDICT: CODE IS REJECTED if there are major security concerns.
        Otherwise, put VERDICT: CODE IS CONDITIONALLY ACCEPTED.
            
        Include a summary rating the below 3 criteria out of 5 stars. Then, get the average rating.
            
        Review this git diff and assess:
        1. PEP-8 Compliance
        2. Possible bugs
        3. Possible security considerations
            
        Include the suggested code changes.

        After your review, add a section called INLINE COMMENTS in this exact format, one per line:
        INLINE::filename.py::42::Your comment about this specific line
        
        Diff:
        {diff}"""
    review = ask_model(input)

    if not review:
        raise ValueError("No review received from the server")

except (requests.RequestException, KeyError, ValueError) as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# --- Get latest commit SHA ---
try:
    gh_token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = os.environ["PR_NUMBER"]

    pr_data = requests.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
        headers={
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json"
        }
    ).json()
    commit_sha = pr_data["head"]["sha"]
    print(f"Latest commit SHA: {commit_sha}")

except KeyError as e:
    print(f"❌ Missing environment variable: {e}")
    sys.exit(1)

# --- Post main review comment ---
try:
    print("Now posting to the PR thread...")

    # Split review body from inline comments
    review_body = review.split("INLINE COMMENTS")[0].strip() if "INLINE COMMENTS" in review else review

    result = requests.post(
        f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
        headers={
            "Authorization": f"Bearer {gh_token}",
            "Accept": "application/vnd.github+json"
        },
        json={"body": f"## 🚔 PR Police Report\n\n{review_body}"}
    )

    print(f"GitHub API status: {result.status_code}")
    if result.status_code == 201:
        print("✅ Posted main review successfully")
    else:
        print(f"❌ Failed: {result.text}")
        sys.exit(1)

except KeyError as e:
    print(f"❌ Missing environment variable: {e}")
    sys.exit(1)

# --- Post inline comments ---
inline_pattern = re.compile(r'INLINE::(.+?)::(\d+)::(.+)', re.IGNORECASE)
inline_matches = inline_pattern.findall(review)

if inline_matches:
    print(f"Found {len(inline_matches)} inline comments, posting...")
    for filename, line_num, comment in inline_matches:
        inline_result = requests.post(
            f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments",
            headers={
                "Authorization": f"Bearer {gh_token}",
                "Accept": "application/vnd.github+json"
            },
            json={
                "body": f"🚔 {comment.strip()}",
                "commit_id": commit_sha,
                "path": filename.strip(),
                "line": int(line_num),
                "side": "RIGHT"
            }
        )
        if inline_result.status_code == 201:
            print(f"✅ Inline comment posted on {filename}:{line_num}")
        else:
            # Don't fail the whole run if one inline comment fails
            print(f"⚠️ Could not post inline on {filename}:{line_num} — {inline_result.text}")
else:
    print("No inline comments found in review.")

# --- Check verdict ---
if "VERDICT: CODE IS REJECTED" in review.upper().split("\n")[0]:
    print("Code has been rejected")
    sys.exit(1)
else:
    print("Code has been accepted")
    sys.exit(0)

# --- Write PR description if it's empty ---
print("Attempting to populate PR description")
pr = requests.get(
    f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
    headers={"Authorization": f"Bearer {gh_token}"}
).json()

print(pr)

if not pr["body"]:
    generated_description = ask_model(f"Write a concise PR description for this diff:\n{diff}")
    print(generated_description)

result = requests.patch(
    f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
    headers={"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json"},
    json={"body": generated_description}
)

print(f"GitHub API status: {result.status_code}")
if result.status_code == 200:  # PATCH returns 200, not 201
    print("✅ PR description updated successfully")
else:
    print(f"❌ Failed to update description: {result.text}")


