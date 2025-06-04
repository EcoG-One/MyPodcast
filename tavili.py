import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
# Set up your OpenAI API key
TAVILI_KEY = os.getenv("TAVILI_KEY")
client = TavilyClient(TAVILI_KEY)

def tavili_answer(topic):
    response = client.search(
        query=topic,
        topic="news",
        time_range="month",
        include_answer="basic"
    )
    print(response['answer'])
    return response['answer']

