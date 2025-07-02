from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from configs.settings import settings
from utils import scrapers
from utils import cleaned_text_lines

# def search_google(query):
#     search = GoogleSearchAPIWrapper(k=2,google_api_key=settings.GOOGLE_API_KEY,google_cse_id=settings.GOOGLE_CSE_ID)
#     search_results = search.results(query,num_results=3)
#     tools = [Tool(name="Google Search", func=search.run, description="Google Search")]
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.0-flash",
#         google_api_key=settings.GEMINI_API_KEY,
#         temperature=0.3
#     )

#     agent = initialize_agent(tools,llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False)
#     return agent.run(query)



def search_google(query):
    search = GoogleSearchAPIWrapper(k=3, google_api_key=settings.GOOGLE_API_KEY, google_cse_id=settings.GOOGLE_CSE_ID)
    search_results = search.results(query,num_results=3)
    print(search_results)
    if not search_results:
        return "No results found."
    
    url = search_results[0].get("link",None)
    scraped_data=None
    if url:
        scraped_data = scrapers.scrape_website(url)
    with open('output.txt','w', encoding='utf-8') as f:
        f.write(scraped_data)

    
    combined_snippets = "\n".join([result.get("snippet", "") for result in search_results])
    print("combined_sjippets",combined_snippets)
    print(30*'*')
    print(scraped_data)
    prompt = f"""
    You are a smart assistant. Using the following search data or snippets provided, answer the user query:
    ---
    data:{scraped_data}
    {combined_snippets}
    ---
    User query: {query}
    Give a concise and clear answer based only on the search content above.
    """

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )

    response = llm.invoke(prompt)
    return response.content
