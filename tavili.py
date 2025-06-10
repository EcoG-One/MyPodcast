import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
# Set up your OpenAI API key
TAVILI_KEY = os.getenv("TAVILI_KEY")
client = TavilyClient(TAVILI_KEY)

def tavili_answer(topic):
    """
    Gets the latest news about the topic using the Tavili API
    the time frame for the news is the last month
    :param topic: the Podcast topic
    :return: text with the latest news about the topic
    """
    response = client.search(
        query=topic,
        topic="news",
        time_range="month",
        include_answer="basic"
    )
    print(response['answer'])
    return response['answer']

