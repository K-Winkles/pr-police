import os
import requests
import sys

# --- Get diff ---
try:
    with open('pr_police/pr_diff.txt', 'r') as file:
        diff = file.read()
except FileNotFoundError:
    print("❌ Diff file not found")
    sys.exit(1)

# --- Get review from Ollama ---
try:
    ollama_api_key = os.getenv('OLLAMA_API_KEY')
    if not ollama_api_key:
        raise ValueError("OLLAMA_API_KEY environment variable is not set")

    prompt = f"""You are a senior code reviewer. Review this git diff and assess:
    1. PEP-8 Compliance
    2. Possible bugs
    3. Possible security considerations
    4. Suggestions for improvement with fully rewritten code

    At the top of your answer, include a verdict wherein if there are any obvious issues, say CODE IS REJECTED.
    Otherwise, say CODE IS CONDITIONALLY ACCEPTED.

    Diff:
    {diff}
    """

    headers = {'Authorization': f'Bearer {ollama_api_key}'}
    response = requests.post('https://api.ollama.com/review', headers=headers, data={'prompt': prompt})
    response.raise_for_status()
    review = response.json().get('review', '')

except KeyError as e:
    print(f"❌ Missing environment variable: {e}")
    sys.exit(1)
except requests.RequestException as e:
    print(f"❌ Error making request to Ollama: {e}")
    sys.exit(1)
except ValueError as e:
    print(f"❌ {e}")
    sys.exit(1)

# --- Check if code is rejected or conditionally accepted ---
if review and "CODE IS REJECTED" in review.upper():
    print("This code has been rejected")
    sys.exit(1)
else:
    print("This code has been conditionally accepted")
    sys.exit(0)