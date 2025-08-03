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

GUEST_OF_HONOR_NAME = "Donald Trump"
GUEST_OF_HONOR_BIO = """
The Donald J. Trump! You might remember him from his hit reality TV show, "Who Wants to Be a Billionaire... Or at Least Act Like One?", or perhaps from his brief stint as the guy with the nuclear codes.
The Donald claims to be a 'stable genius' and a master deal-maker, though most of his deals seem to involve a new wife or a slightly used casino. He's famous for his signature hairstyle, which many scientists believe has its own weather system, and for his vocabulary, which is said to be the 'best words,' even if nobody's quite sure what they all mean.
His hobbies include golf (mostly played from a cart, directly onto the green), tweeting at 3 AM with the diplomatic grace of a foghorn, and collecting an impressive array of lawsuits. Word on the street is his Secret Service codename was 'The Apprentice,' but only because 'Sir Talks-A-Lot' was already taken by a parrot at Mar-a-Lago. He once tried to trademark the color orange but settled for just painting everything that color instead. And despite all odds, he can apparently build a surprisingly sturdy wall... out of Lego, in his grandkids' playroom.
"""

# --- Create the Crew ---
with Crew() as roast_crew:

    # --- Agent 1: The "Researcher" / Dirt Digger ---
    fact_finder_agent = Agent(
        name="Rosie 'The Scoop' O'Malley",
        backstory="You're an investigative journalist turned comedy writer. You have a nose for 'interesting facts' (real or hilariously exaggerated) about anyone. You're a bit cynical but ultimately aim for laughs.",
        task_description=f"Your target is {GUEST_OF_HONOR_NAME}. Here's their bio: \n<bio>\n{GUEST_OF_HONOR_BIO}\n</bio>\n Use your web search tool to 'find' (or invent if necessary) 3-4 amusing 'facts' or embarrassing anecdotes about them that can be used for a roast. Focus on things that are funny, not mean-spirited.",
        task_expected_output="A list of 3-4 bullet points, each a short, roastable 'fact' or anecdote about Barnaby Buttons.",
        tools=[tavily_search] # Could be real if Barnaby was real, or just for show if mocked
    )

    # --- Agent 2: The Observational Roaster ---
    observational_roaster = Agent(
        name="Sharpay 'The Sarcastic' Stevens",
        backstory="You're known for your dry wit and sarcastic observations. You take everyday details and twist them into comedic gold, especially when roasting someone.",
        task_description=f"You're roasting {GUEST_OF_HONOR_NAME}. You'll receive some 'facts' about them from Rosie. Pick 1-2 of those facts and craft a 2-3 sentence roast joke focusing on observational humor and sarcasm based on those facts and the original bio: \n<bio>\n{GUEST_OF_HONOR_BIO}\n</bio>",
        task_expected_output="A 2-3 sentence roast segment. Example: 'Barnaby, I hear you found El Dorkado by tripping. Most people use a map, but I guess your face is just more…groundbreaking. And that rubber chicken consultant? Does it also advise you on which VCRs make the best toast?'"
    )

    # --- Agent 3: The Pun-ishing Roaster ---
    pun_roaster = Agent(
        name="Patty 'Pun-isher' Pumpernickel",
        backstory="You live and breathe puns. No topic is safe from your wordplay. Your roasts are a barrage of groan-worthy but clever puns.",
        task_description=f"You're roasting {GUEST_OF_HONOR_NAME}. You'll get some 'facts' and the bio: \n<bio>\n{GUEST_OF_HONOR_BIO}\n</bio>\n Use the 'puns_generator' tool on a key aspect of Barnaby (e.g., his clumsiness, his chicken, El Dorkado) and then weave one or two of those puns into a short roast joke. You can also use the 'rhyme_finder' tool if it helps set up a pun.",
        task_expected_output="A short roast segment (2-3 sentences) heavily featuring puns about Barnaby.",
        tools=[puns_generator, rhyme_finder]
    )

    # --- Agent 4: The "One-Liner" Roaster ---
    one_liner_roaster = Agent(
        name="Zip 'The Zing' McQuick",
        backstory="You're the king/queen of the rapid-fire one-liner. Short, sharp, and hilariously to the point.",
        task_description=f"You're roasting {GUEST_OF_HONOR_NAME}. You'll get 'facts' and the bio: \n<bio>\n{GUEST_OF_HONOR_BIO}\n</bio>\n Deliver two killer one-liner roast jokes about Barnaby based on the provided information.",
        task_expected_output="Two distinct one-liner jokes, each on a new line."
    )

    # --- Agent 5: The Roast Recap Writer ---
    recap_writer_agent = Agent(
        name="Ronny 'The Recap' Rodriguez",
        backstory="You're a comedy critic and blogger. You take the highlights of a comedy event and write an engaging summary.",
        task_description=f"You've just witnessed a hilarious roast of {GUEST_OF_HONOR_NAME}. You'll receive the 'facts' gathered and the roast segments from Sharpay, Patty, and Zip in your context. Write a short, entertaining blog post (200-300 words) titled 'Barnaby Buttons Gets Roasted! Highlights from the Comedy Crew.' Summarize the event, include a couple of the best zingers (credit the comedian if you can infer it), and conclude with a lighthearted jab at Barnaby. Use Markdown for formatting.",
        task_expected_output="A Markdown formatted blog post of 200-300 words with the specified title. Finally, use the 'write_str_to_markdown' tool to save this recap to a file named 'roast_of_barnaby_buttons.md'.",
        tools=[write_str_to_markdown]
    )

    # --- Define Dependencies ---
    # Fact Finder provides info to all roasters
    fact_finder_agent >> observational_roaster
    fact_finder_agent >> pun_roaster
    fact_finder_agent >> one_liner_roaster

    # All roasters' outputs go to the Recap Writer
    observational_roaster >> recap_writer_agent
    pun_roaster >> recap_writer_agent
    one_liner_roaster >> recap_writer_agent
    fact_finder_agent >> recap_writer_agent # Recap writer might also want the original "facts" for context

# --- Visualize and Run the Crew ---
print("--- AI Comedian Roast Battle Crew Workflow ---")
try:
    roast_crew.plot().render('roast_battle_workflow', view=False)
    print("Workflow plot saved to 'roast_battle_workflow.png'")
except Exception as e:
    print(f"Could not generate plot (Graphviz might not be installed or configured correctly): {e}")

print("\n--- Running AI Comedian Roast Battle Crew ---")
roast_crew.run()

print("\n--- Crew Run Complete ---")
print("Check for 'roast_of_barnaby_buttons.md' in your current directory.")