import requests
import openai
import json
import os
import re

# Load environment variables for the API key
from dotenv import load_dotenv
load_dotenv()

def searxng_search(query: str):
    """
    Performs a search using a local SearXNG instance.
    """
    url = "http://localhost:8080/search"
    params = {"q": query, "format": "json"}
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; SearXNG-Client/1.0; +https://searxng.org)",
        "Accept": "application/json"
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Couldn't fetch results from SearXNG: {e}")
        return []

def get_openrouter_client():
    """
    Initializes and returns the OpenAI client configured for OpenRouter.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set the OPENROUTER_API_KEY environment variable.")
    
    return openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def generate_subqueries(user_input):
    """
    Uses the DeepSeek model via OpenRouter to generate search subqueries.
    """
    client = get_openrouter_client()
    prompt = f"Based on the following user query, generate a list of 3-5 concise search queries to find relevant information. Respond with a JSON array of strings only. User query: {user_input}"
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[{"role": "user", "content": prompt}],
        )
        subqueries_json = response.choices[0].message.content
        # Extract the JSON array from the response, as the model may add extra text
        match = re.search(r'\[.*?\]', subqueries_json, re.DOTALL)
        if match:
            subqueries = json.loads(match.group(0))
            return subqueries
        return [user_input]  # Fallback to original input if JSON is not found
    except Exception as e:
        print(f"[ERROR] Failed to generate subqueries with OpenRouter: {e}")
        return [user_input]

def generate_final_response(user_input, search_results_text, chat_history):
    """
    Generates the final, framed response based on user input and search results.
    """
    client = get_openrouter_client()
    history_prompt = " ".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    prompt = f"You are a helpful assistant. You have access to the following search results:\n\n{search_results_text}\n\nBased on this information and the following conversation history, answer the user's latest query. Conversation History: {history_prompt}\nUser's latest query: {user_input}"
    
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Oops, I ran into a problem generating the final response: {e}"

def get_llm_response(messages, websearch_enabled=False):
    """
    Orchestrates the RAG process with SearXNG and DeepSeek.
    """
    try:
        user_input = messages[-1]['content']
        search_results_text = ""
        
        if websearch_enabled:
            # Step 1: Generate subqueries from user input
            subqueries = generate_subqueries(user_input)
            
            # Step 2: Perform search for each subquery
            all_results = []
            for query in subqueries:
                results = searxng_search(query)
                all_results.extend(results)
            
            # Step 3: Format search results for the LLM
            search_results_text = "Search Results:\n\n"
            if not all_results:
                search_results_text = "No relevant search results were found."
            else:
                for i, result in enumerate(all_results[:5]): # Limit to top 5 results
                    search_results_text += f"Result {i+1}: Title: {result.get('title', '')}\nURL: {result.get('url', '')}\nContent: {result.get('content', '')[:200]}...\n\n"
        
        # Step 4: Generate final response based on history and search results
        response_content = generate_final_response(user_input, search_results_text, messages)
        
        return {"status": "success", "response": response_content}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

