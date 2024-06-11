# Introduction 
* This Repo contains multiple PoC projects for AI using Azure OpenAI and langchain

# Getting Started
* Install Python 3.11 (make sure to also install pip)
* Make sure python/Scripts folder is in the path
* Install Poetry (pip install poetry)
* In root of the project run poetry shell
* Then poetry install
* make a .env file next to the .env.example file with the contents of the .env.example file

## Optional
* In VS Code, open the gear > profiles > create profile > copy from python
* in VS Code -> on a python file -> in bottom right -> make sure you select the venv created by poetry as language mode

# Running Projects
* Chatbot: streamlit run ./app/chat_with_history.py
* Index loading for coman: python ./app/test-import-coman.py
* API with swagger: fastapi dev ./app/main.py
* In discovery are all the test projects a jupyter notebook (make sure to select the venv as python interpreter when running)

# Generate requirements from poetry 
* poetry export --without-hashes --format=requirements.txt > requirements.txt
