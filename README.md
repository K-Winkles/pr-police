# PR Police Boilerplate

Simple PR reviewer. No voodoo or magic happening here.

1. All PR Police files are in `pr_police`.
    * workflows naturally contains the Github action workflow
    * `app.py` contains the script to serve the LLM locally
    * `review.py` is what the workflow calls to forward the PR code diff to the LLM
    * `send.py` is just a test script to check if the model is operational
2. All actual project files will be placed anywhere but the `pr_police` folder.