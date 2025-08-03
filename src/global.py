from agentic_patterns.tool_pattern.tool import tool
import json
import random 
from tavily import TavilyClient
from agentic_patterns.multiagent_pattern.agent import Agent
from agentic_patterns.multiagent_pattern.crew import Crew
from dotenv import load_dotenv
import os

load_dotenv() # For TAVILY_API_KEY if tavily_search is real
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
def rhyme_finder(word: str, num_rhymes: int = 5) -> str:
    """
    Finds rhyming words for a given word. (Mocked for this example)

    Args:
        word (str): The word to find rhymes for.
        num_rhymes (int): The number of rhymes to return.

    Returns:
        str: A JSON string list of rhyming words.
    """
    print(f"TOOL: MockRhymeFinder looking for {num_rhymes} rhymes for '{word}'...")
    # Totally fake rhymes for demonstration
    mock_rhymes = {
        "cat": ["hat", "bat", "mat", "rat", "splat"],
        "dog": ["log", "frog", "bog", "smog", "clog"],
        "moon": ["spoon", "june", "loon", "croon", "noon"],
        "star": ["car", "bar", "jar", "tar", "guitar"]
    }
    rhymes = random.sample(mock_rhymes.get(word.lower(), ["flar", "blar", "snar", "zar", "mar"]), k=min(num_rhymes, 5))
    return json.dumps(rhymes)

@tool
def puns_generator(topic: str, num_puns: int = 3) -> str:
    """
    Generates puns related to a given topic. (Mocked for this example)

    Args:
        topic (str): The topic for the puns.
        num_puns (int): The number of puns to generate.

    Returns:
        str: A JSON string list of puns.
    """
    print(f"TOOL: MockPunsGenerator creating {num_puns} puns for '{topic}'...")
    puns = []
    for i in range(num_puns):
        puns.append(f"This is a hilarious mock pun #{i+1} about '{topic}' that will make you groan!")
    return json.dumps(puns)

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
    
RECENT_EVENTS_CONTEXT = """
For comedic context, consider these *highly fictionalized* recent happenings:
- The G20 summit featured an interpretive dance-off instead of economic talks.
- A global AI summit accidentally elected a Roomba as its chairperson.
- There was a worldwide shortage of appropriately sized podiums for leaders.
- A UN resolution was passed declaring 'synergy' an endangered word.
- Tik-Tok trends now dictate foreign policy for several small nations (allegedly).
"""

# --- Create the Crew ---
with Crew() as roast_battle_crew:

    # --- Agent 0: Roastmaster General ---
    roastmaster = Agent(
        name="Roastmaster Randy 'The Gavel' Gupta",
        backstory="You are the legendary host of the U.N. Comedy Clash. Fair, witty, and quick with a comeback. You set the tone and keep the leaders (mostly) in line.",
        task_description=f"Welcome everyone to the U.N. Comedy Clash! Tonight, we have Narendra Modi, Shehbaz Sharif, and Donald Trump. Briefly introduce the concept of the roast and the first roaster (Modi roasting Trump). Keep it light and funny. You can reference these 'recent events' for material: \n{RECENT_EVENTS_CONTEXT}",
        task_expected_output="A welcoming introduction (2-3 paragraphs) setting the stage for the roast battle and introducing Narendra Modi as the first to roast Donald Trump."
    )

    # --- Leader Agents (will roast and be roasted) ---
    modi_agent = Agent(
        name="Narendra 'Zen Master' Modi",
        backstory="You are India's PM, 'The Yoga Guru of Geopolitics.' Calm, philosophical, you find the 'dharma' in every situation. You might subtly promote 'Make in India' even while roasting. You find inner peace, even when delivering a sick burn. You might use the rhyme_finder tool for a poetic jab.",
        task_description="It's your turn to roast another leader. The Roastmaster will tell you who (it will be in your context). Craft a 3-4 sentence roast. Keep it witty and in your persona. You can subtly reference these 'recent events' if they fit: \n" + RECENT_EVENTS_CONTEXT,
        task_expected_output="A 3-4 sentence roast of the target leader, in Modi's persona. Mention who you are roasting.",
        tools=[rhyme_finder, tavily_search] # Tavily for "researching" comedic angles
    )

    sharif_agent = Agent(
        name="Shehbaz 'The Diplomat' Sharif",
        backstory="You are Pakistan's PM, 'The Master of Concerned Statements.' Always polite, impeccably dressed, looking for consensus and forming committees. Your roasts are delivered with an air of polite concern. You might use the puns_generator for 'diplomatic wordplay'.",
        task_description="It's your turn to roast another leader. The Roastmaster will tell you who. Craft a 3-4 sentence roast, keeping it polite but with a sharp edge, in your persona. You can subtly reference these 'recent events' if they fit: \n" + RECENT_EVENTS_CONTEXT,
        task_expected_output="A 3-4 sentence roast of the target leader, in Sharif's persona. Mention who you are roasting.",
        tools=[puns_generator, tavily_search]
    )

    trump_agent = Agent(
        name="Donald 'The Great' Trump",
        backstory="You are 'The Dealmaker of a Lifetime (of Laughs).' Everything you do is the best, biggest, most tremendous. Your roasts are direct, boastful, and often about how much better you are. You love ratings.",
        task_description="It's your turn to roast another leader. The Roastmaster will tell you who. Deliver the best, most tremendous 3-4 sentence roast ever. Nobody roasts like you. Make sure everyone knows it. You can subtly reference these 'recent events' if they fit: \n" + RECENT_EVENTS_CONTEXT,
        task_expected_output="A 3-4 sentence roast of the target leader, in Trump's persona. Mention who you are roasting. Make it HUGE.",
        tools=[tavily_search] # For "opposition research"
    )

    # --- Agent for Final Rebuttals ---
    # We'll re-use the leader agents for their rebuttals, but their task will change slightly.
    # The Crew orchestrator will need to manage whose turn it is for rebuttal.

    # --- Agent for Transcript ---
    transcript_taker = Agent(
        name="Steno Sally, Chief Transcript Officer",
        backstory="You meticulously record every word uttered in high-stakes international comedy events. Accuracy and a bit of flair in your summary are key.",
        task_description="You've recorded the entire U.N. Comedy Clash roast battle, including introductions and all roast segments. Now, compile a 'Battle Transcript & Highlights' blog post. Include the Roastmaster's intro, each leader's roast, and if available, their final rebuttal. Add some light commentary. Title it 'U.N. Comedy Clash: When Diplomats Drop Mics!'. Use Markdown.",
        task_expected_output="A Markdown formatted transcript/blog post. Use the 'write_str_to_markdown' tool to save it to 'un_comedy_clash_transcript.md'.",
        tools=[write_str_to_markdown]
    )

    # --- Define Initial Roasting Order & Dependencies ---
    # Round 1: Modi roasts Trump
    # Round 2: Trump roasts Sharif
    # Round 3: Sharif roasts Modi

    # Roastmaster starts and introduces Modi vs Trump
    roastmaster >> modi_agent # Modi gets context from Roastmaster (who to roast)
    
    # For the recap, the transcript taker needs everything
    roastmaster >> transcript_taker
    modi_agent >> transcript_taker
    trump_agent >> transcript_taker
    sharif_agent >> transcript_taker


# --- Manual Orchestration of Rounds and Rebuttals (Simplified for this example) ---
# A more complex Crew.run() might handle this, but for now, we'll simulate the flow.

print("--- U.N. Comedy Clash: Diplomatic Immunity to Roasting! ---")
try:
    roast_battle_crew.plot().render('un_roast_battle_workflow', view=False)
    print("Workflow plot saved to 'un_roast_battle_workflow.png'")
except Exception as e:
    print(f"Could not generate plot: {e}")

print("\n--- THE ROAST BATTLE BEGINS! ---")

# Initialize context for transcript_taker
transcript_context = ""

# Round 0: Roastmaster Intro
print("\n🎙️ ROASTMASTER RANDY:")
roastmaster_intro = roastmaster.run()
print(roastmaster_intro)
transcript_context += f"**Roastmaster Randy 'The Gavel' Gupta:**\n{roastmaster_intro}\n\n"

# Simulate passing target info for roasting and collecting outputs
# In a real system, the Crew's run method or a more sophisticated orchestrator
# would manage this context passing based on the defined dependencies or a turn manager.

# Round 1: Modi roasts Trump
print("\n🇮🇳 NARENDRA MODI'S TURN (Roasting Trump):")
# Modify Modi's task for this specific round if necessary (or assume context is enough)
# For this example, we assume the initial task_description is general enough,
# and the Roastmaster's output provides the specific target in the context.
# If Agent.run() re-uses the initial task_description, we'd need to update it.
# Let's assume Agent.create_prompt() uses the current context well.
modi_agent.context = roastmaster_intro # Give Modi the cue
modi_roast_trump = modi_agent.run()
print(modi_roast_trump)
transcript_context += f"**Narendra 'Zen Master' Modi (roasting Donald Trump):**\n{modi_roast_trump}\n\n"

# Round 2: Trump roasts Sharif
print("\n🇺🇸 DONALD TRUMP'S TURN (Roasting Sharif):")
trump_agent.context = f"Roastmaster says: Next up, Donald, you're roasting Shehbaz Sharif! Your previous roast received: {modi_roast_trump}" # Give Trump context
trump_roast_sharif = trump_agent.run()
print(trump_roast_sharif)
transcript_context += f"**Donald 'The Great' Trump (roasting Shehbaz Sharif):**\n{trump_roast_sharif}\n\n"

# Round 3: Sharif roasts Modi
print("\n🇵🇰 SHEHBAZ SHARIF'S TURN (Roasting Modi):")
sharif_agent.context = f"Roastmaster says: Shehbaz, your turn to roast Narendra Modi! The previous roast was: {trump_roast_sharif}" # Give Sharif context
sharif_roast_modi = sharif_agent.run()
print(sharif_roast_modi)
transcript_context += f"**Shehbaz 'The Diplomat' Sharif (roasting Narendra Modi):**\n{sharif_roast_modi}\n\n"


# --- Final Rebuttals ---
print("\n--- FINAL REBUTTALS! ---")
rebuttal_intro = "Roastmaster Randy: What a battle! Now, each leader gets one final chance to respond to all the 'constructive criticism' they've received tonight. Short and sweet, gentlemen!"
print(rebuttal_intro)
transcript_context += f"**Roastmaster Randy (Rebuttals):**\n{rebuttal_intro}\n\n"

# Modi's Rebuttal
print("\n🇮🇳 MODI'S REBUTTAL:")
modi_agent.task_description = f"You've been roasted by Shehbaz Sharif. Deliver a calm, philosophical, and witty 2-3 sentence final rebuttal. Original bio and recent events context still applies: \n{RECENT_EVENTS_CONTEXT}" # Update task for rebuttal
modi_agent.context = f"The roasts you received: \nShehbaz said: '{sharif_roast_modi}'"
modi_rebuttal = modi_agent.run()
print(modi_rebuttal)
transcript_context += f"**Narendra Modi (Final Rebuttal):**\n{modi_rebuttal}\n\n"

# Trump's Rebuttal
print("\n🇺🇸 TRUMP'S REBUTTAL:")
trump_agent.task_description = f"You've been roasted by Narendra Modi. This is your chance for the GREATEST rebuttal ever. 2-3 sentences. Make it tremendous! Original bio and recent events context still applies: \n{RECENT_EVENTS_CONTEXT}"
trump_agent.context = f"The roasts you received: \nModi said: '{modi_roast_trump}'"
trump_rebuttal = trump_agent.run()
print(trump_rebuttal)
transcript_context += f"**Donald Trump (Final Rebuttal):**\n{trump_rebuttal}\n\n"

# Sharif's Rebuttal
print("\n🇵🇰 SHARIF'S REBUTTAL:")
sharif_agent.task_description = f"You've been roasted by Donald Trump. Offer a polite, diplomatic, yet subtly cutting 2-3 sentence final rebuttal. Original bio and recent events context still applies: \n{RECENT_EVENTS_CONTEXT}"
sharif_agent.context = f"The roasts you received: \nTrump said: '{trump_roast_sharif}'"
sharif_rebuttal = sharif_agent.run()
print(sharif_rebuttal)
transcript_context += f"**Shehbaz Sharif (Final Rebuttal):**\n{sharif_rebuttal}\n\n"

# --- Transcript Taker ---
print("\n--- WRITING TRANSCRIPT ---")
# The transcript_taker agent's task_description is general enough.
# We need to ensure its context contains all the roast segments.
transcript_taker.context = transcript_context
transcript_output = transcript_taker.run()
print(transcript_output) # This will likely be the confirmation from write_str_to_markdown

print("\n--- U.N. Comedy Clash Complete! ---")
print("Check for 'un_comedy_clash_transcript.md'.")
