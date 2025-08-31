# routes/LLM.py
from flask import Blueprint, request, jsonify
import requests
import openai
import json
import os
import re
from dotenv import load_dotenv

# Fix imports - use absolute path
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database_utils import DatabaseManager  # Changed from database_utils to database

load_dotenv()
db_manager = DatabaseManager()
llm_bp = Blueprint('llm_bp', __name__)

# REMOVE all SQLAlchemy functions (save_chat_to_db, get_chat_history, etc.)
# They conflict with DatabaseManager

# Your existing LLM functions here (searxng_search, get_openrouter_client, etc.)
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

# Blueprint routes
@llm_bp.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        report_data = request.json
        
        # Format the prompt for the LLM
        prompt = f"""Generate a comprehensive green hydrogen production feasibility report based on the following analysis:

Location: {report_data['location']}
Overall Feasibility: {report_data['feasibility']}
Recommended Technology: {report_data['recommended_technology']}

Suitability Scores:
- Solar Electrolysis: {report_data['suitability_scores']['solar_electrolysis']}
- Wind Electrolysis: {report_data['suitability_scores']['wind_electrolysis']}
- Thermal with CCS: {report_data['suitability_scores']['thermal_with_ccs']}

Regional Advantages:
{chr(10).join(['- ' + adv for adv in report_data['regional_advantages']])}

Please provide a detailed analysis including:
1. Executive summary with key findings
2. Detailed technology comparison and recommendations
3. Economic viability assessment with potential ROI
4. Infrastructure requirements and estimated costs
5. Environmental impact analysis
6. Implementation timeline (short, medium, long-term)
7. Risk assessment and mitigation strategies
8. Specific recommendations for this location

Format the response using markdown with clear section headings."""
        
        # Use your existing LLM function to generate the report
        llm_response = get_llm_response(
            [{"role": "user", "content": prompt}],
            websearch_enabled=True
        )
        
        if 'error' in llm_response:
            return jsonify({'status': 'error', 'error': llm_response['error']})
        
        # Convert feasibility score to float
        feasibility_score = None
        if 'feasibility' in report_data:
            try:
                feasibility_score = float(report_data['feasibility'].replace('%', '').strip())
            except (ValueError, AttributeError):
                pass
        
        # Save to database using DatabaseManager
        session_id = db_manager.save_chat_session({
            'location': report_data.get('location', 'Unknown Location'),
            'latitude': report_data.get('latitude'),
            'longitude': report_data.get('longitude'),
            'feasibility': feasibility_score,
            'recommended_technology': report_data.get('recommended_technology'),
            'session_id': report_data.get('session_id')
        })
        
        if session_id:
            # Save the prompt and response
            db_manager.save_chat_message(session_id, 'user', prompt[:4000])
            db_manager.save_chat_message(session_id, 'assistant', llm_response.get('response', '')[:4000], is_report=True)
        
        return jsonify({
            'status': 'success', 
            'report': llm_response.get('response', 'No report generated'),
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@llm_bp.route('/ask-question', methods=['POST'])
def ask_question():
    try:
        data = request.json
        question = data['question']
        report_data = data.get('report_data', {})
        session_id = data.get('session_id')
        
        # Create context from the report data
        context = f"""
        Based on the previous hydrogen production feasibility analysis for {report_data.get('location', 'this location')}:
        - Overall Feasibility: {report_data.get('feasibility', 'N/A')}
        - Recommended Technology: {report_data.get('recommended_technology', 'N/A')}
        - Regional Advantages: {', '.join(report_data.get('regional_advantages', []))}
        
        Please answer the following question: {question}
        """
        
        # Use your existing LLM function
        llm_response = get_llm_response(
            [{"role": "user", "content": context}],
            websearch_enabled=True
        )
        
        if 'error' in llm_response:
            return jsonify({'status': 'error', 'error': llm_response['error']})
        
        # Save to database if we have a session_id
        if session_id:
            db_manager.save_chat_message(session_id, 'user', question[:4000])
            db_manager.save_chat_message(session_id, 'assistant', llm_response.get('response', '')[:4000])
        
        return jsonify({
            'status': 'success', 
            'answer': llm_response.get('response', 'No answer generated'),
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

# REMOVE all SQLAlchemy-based functions below this line
# Remove: get_recent_chat_history, format_recent_messages, summarize_conversation
# These functions use ChatMessage.query which conflicts with DatabaseManager

# If you need these functions, create DatabaseManager versions:
def get_recent_chat_history(session_id, max_messages=6):
    """Get optimized chat history using DatabaseManager"""
    try:
        if not session_id:
            return []
            
        # Use DatabaseManager to get messages
        messages = db_manager.get_recent_chat_history(session_id, max_messages)
        return messages
            
    except Exception as e:
        print(f"Error getting optimized chat history: {e}")
        return []

def summarize_conversation(session_id):
    """Create a summary of long conversations using DatabaseManager"""
    try:
        # Get all messages for this session using DatabaseManager
        messages = db_manager.get_chat_messages(session_id)
        
        if len(messages) <= 10:  # No need to summarize short conversations
            return None
            
        # Prepare conversation for summarization
        conversation_text = "\n".join([
            f"{msg['role'].capitalize()}: {msg['content'][:200]}"
            for msg in messages
        ])
        
        summary_prompt = f"""
        Summarize this conversation about hydrogen production feasibility analysis.
        Focus on key decisions, questions asked, and recommendations made.
        Keep the summary under 200 words.
        
        Conversation:
        {conversation_text[:4000]}  # Limit input length
        """
        
        # Get summary from LLM
        summary_response = get_llm_response(
            [{"role": "user", "content": summary_prompt}],
            websearch_enabled=False
        )
        
        if 'error' not in summary_response:
            return summary_response.get('response', '')
        
        return None
        
    except Exception as e:
        print(f"Error summarizing conversation: {e}")
        return None