from agentic_patterns.tool_pattern.tool import tool
from tavily import TavilyClient
import os
import json
from agentic_patterns.multiagent_pattern.agent import Agent
from agentic_patterns.multiagent_pattern.crew import Crew
# Assuming tavily_search and write_str_to_markdown tools are defined above
# and your Agent, Crew, tool decorator are in their respective modules.
from dotenv import load_dotenv # If you're using a .env file for TAVILY_API_KEY

load_dotenv() # Load environment variables (like TAVILY_API_KEY)

# Ensure your TAVILY_API_KEY is set as an environment variable
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable not set.")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

@tool
def tavily_search(query: str, search_depth: str = "basic", max_results: int = 3, include_domains: list[str] | None = None, exclude_domains: list[str] | None = None) -> str:
    """
    Performs a web search using the Tavily API and returns a list of findings.

    Args:
        query (str): The search query.
        search_depth (str, optional): The depth of the search. Can be "basic" or "advanced". Defaults to "basic".
        max_results (int, optional): The maximum number of search results to return. Defaults to 3.
        include_domains (list[str] | None, optional): A list of domains to exclusively search within. Defaults to None.
        exclude_domains (list[str] | None, optional): A list of domains to exclude from the search. Defaults to None.

    Returns:
        str: A JSON string representing a list of search results (title, url, content, score, raw_content).
    """
    print(f"TOOL: Performing Tavily search for '{query}' (max_results: {max_results}, depth: {search_depth})...")
    try:
        response = tavily_client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        # Tavily returns a dictionary with a 'results' key, which is a list of dicts.
        # We'll return this list of result dictionaries as a JSON string.
        return json.dumps(response.get("results", []))
    except Exception as e:
        print(f"TOOL ERROR: Tavily search failed for query '{query}': {e}")
        return json.dumps([{"error": str(e)}]) # Return error info as JSON

@tool
def write_str_to_markdown(string_data: str, md_filename: str) -> str:
    """
    Writes a string to a Markdown (.md) file.
    If the file already exists, it will be overwritten.

    Args:
        string_data (str): The string containing the Markdown data.
        md_filename (str): The name of the Markdown file (e.g., 'travel_itinerary.md').
    
    Returns:
        str: Confirmation message.
    """
    try:
        with open(md_filename, mode='w', encoding='utf-8') as file:
            file.write(string_data)
        confirmation_message = f"Markdown data successfully written to {md_filename}"
        print(f"TOOL: {confirmation_message}")
        return confirmation_message
    except Exception as e:
        error_message = f"TOOL ERROR: Failed to write to {md_filename}: {e}"
        print(error_message)
        return error_message
    
# --- User Input ---
USER_PREFERENCES_PROMPT = """
I'm looking for a 5-day adventurous trip to a mountainous region in Europe during the summer.
I'm moderately fit and enjoy hiking and beautiful scenery. My budget is around $1500 excluding flights.
I prefer unique local experiences over very touristy spots and love trying authentic cuisine.
I'd like to stay in guesthouses or small, charming hotels.
"""

# --- Create the Crew ---
with Crew() as travel_crew:

    # --- Agent 1: Preference Analyst Agent ---
    preference_analyst = Agent(
        name="Travel Preference Analyst",
        backstory="You are an AI expert at meticulously parsing user travel requests to extract key preferences. Your goal is to create a structured summary of these preferences that other agents can easily use.",
        task_description=f"Analyze the following user travel request and extract the key preferences. Present them as a structured list or key-value pairs. User request: \n<user_request>\n{USER_PREFERENCES_PROMPT}\n</user_request>",
        task_expected_output="A structured summary of preferences including: duration, desired travel style (e.g., adventurous, relaxing), destination type (e.g., mountains, beach), preferred continent/region, preferred season/time, fitness level, key activities/interests (e.g., hiking, scenery, local food), budget (excluding flights if specified), accommodation preference, and any other notable desires (e.g., avoid touristy spots)."
    )

    # --- Agent 2: Destination Researcher Agent ---
    destination_researcher = Agent(
        name="Global Destination Scout",
        backstory="You are a seasoned travel researcher with a knack for finding hidden gems and matching them to traveler profiles. You leverage web search extensively.",
        task_description="Based on the provided user preferences (from context), use your web search tool to identify 2-3 specific destinations that would be an excellent match. For each destination, provide a brief description (2-3 sentences), list 2-3 pros, and 1-2 cons relevant to the user's preferences. Cite the source URLs from your search if they seem particularly useful.",
        task_expected_output="A list of 2-3 destination suggestions. Each suggestion should include: \n- Destination Name (City/Region, Country)\n- Brief Description\n- Pros (relevant to user preferences)\n- Cons (relevant to user preferences)\n- (Optional) Key source URLs from search results that support your suggestion.",
        tools=[tavily_search]
    )

    # --- Agent 3: Activity Planner Agent ---
    # For this example, we'll assume the first destination suggested by the Destination Researcher is chosen.
    # A more advanced version could involve user interaction or another agent to make this choice.
    activity_planner = Agent(
        name="Detailed Itinerary Crafter",
        backstory="You are an expert in planning engaging and immersive daily travel activities. You can take a destination and user interests and build a day-by-day plan.",
        task_description="You will receive user preferences and a list of suggested destinations in your context. Focus on the *first* destination suggested. Plan a detailed day-by-day itinerary for the duration specified in the user preferences. For each day, suggest 2-3 activities (e.g., specific hikes, cultural sites, food experiences, viewpoints) that align with the user's interests. Use your web search tool to find specific activities, opening hours if relevant, and local food spots for the chosen destination. Briefly describe each activity.",
        task_expected_output="A day-by-day itinerary. For each day (e.g., Day 1, Day 2, ...):\n- Morning: [Activity suggestion + brief description]\n- Afternoon: [Activity suggestion + brief description]\n- Evening: [Activity suggestion/Restaurant type + brief description]\nEnsure activities align with the user's stated interests and fitness level.",
        tools=[tavily_search]
    )

    # --- Agent 4: Logistics Coordinator Agent ---
    logistics_coordinator = Agent(
        name="Travel Logistics Specialist",
        backstory="You focus on the practicalities of travel, offering advice on accommodation, local transport, and other essential tips to make a trip smoother.",
        task_description="Based on the user preferences, the chosen destination (assume first from the list), and the planned daily activities (all from context), provide logistical advice. Suggest 2-3 types of accommodation that match the user's preference (e.g., 'charming guesthouses', 'well-rated small hotels') and use web search to find general price ranges or specific examples if easily found. Offer 2-3 general tips for local transportation within the destination. Add any other crucial practical tips (e.g., best time to book, local customs to be aware of if prominent).",
        task_expected_output="A section with:\n- Accommodation Suggestions: [Type 1 (e.g., Guesthouses) - general characteristics/price idea; Type 2...]\n- Local Transportation Tips: [Tip 1; Tip 2...]\n- Other Practical Tips: [Tip 1; Tip 2...]",
        tools=[tavily_search]
    )

    # --- Agent 5: Itinerary Compiler Agent ---
    itinerary_compiler = Agent(
        name="Chief Itinerary Publisher",
        backstory="You are an expert at compiling all travel planning components into a single, coherent, well-formatted, and inspiring document.",
        task_description="You will receive the user's initial preferences, the chosen destination details, the day-by-day activity plan, and logistical advice in your context. Combine all this information into a comprehensive travel itinerary. Start with a brief overview/introduction. Then, present the day-by-day plan. Follow with the accommodation and logistics section. Ensure the final document is well-organized and easy to read. Use Markdown for formatting.",
        task_expected_output="A complete travel itinerary in Markdown format. It should include sections for: Introduction/Overview, Daily Itinerary (Day 1, Day 2, etc.), Accommodation Suggestions, Transportation Tips, and Other Practical Tips. Finally, use the 'write_str_to_markdown' tool to save this complete itinerary to a file named 'personalized_travel_itinerary.md'. The tool call should be the last part of your response.",
        tools=[write_str_to_markdown]
    )

    # --- Define Dependencies ---
    preference_analyst >> destination_researcher
    destination_researcher >> activity_planner
    activity_planner >> logistics_coordinator
    # Itinerary Compiler needs info from all previous relevant stages
    preference_analyst >> itinerary_compiler     # For overview and re-stating preferences
    destination_researcher >> itinerary_compiler # For chosen destination details
    activity_planner >> itinerary_compiler       # For the daily plan
    logistics_coordinator >> itinerary_compiler  # For logistics information

# --- Visualize and Run the Crew ---
print("--- Personalized Travel Itinerary Planner Crew Workflow ---")
# Ensure you have graphviz installed and in PATH for plotting to work smoothly
try:
    travel_crew.plot().render('travel_itinerary_workflow', view=False) # view=False to not auto-open
    print("Workflow plot saved to 'travel_itinerary_workflow.png'")
except Exception as e:
    print(f"Could not generate plot (Graphviz might not be installed or configured correctly): {e}")


print("\n--- Running Personalized Travel Itinerary Planner Crew ---")
travel_crew.run()

print("\n--- Crew Run Complete ---")
print("Check for 'personalized_travel_itinerary.md' in your current directory.")