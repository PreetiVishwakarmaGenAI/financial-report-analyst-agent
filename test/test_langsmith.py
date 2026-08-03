from dotenv import load_dotenv

load_dotenv()

import os
from langchain_openai import ChatOpenAI

print(os.getenv("OPENAI_API_KEY"))
print(os.getenv("LANGCHAIN_API_KEY"))
print(os.getenv("LANGCHAIN_PROJECT"))

llm = ChatOpenAI(model="gpt-4.1-mini")

response = llm.invoke("Hello")

print(response.content)