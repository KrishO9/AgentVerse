from agentic_patterns.multiagent_pattern.agent import Agent
from agentic_patterns.multiagent_pattern.crew import Crew
# Assuming write_str_to_txt, web_search, and write_str_to_markdown are defined as above
from agentic_patterns.tool_pattern.tool import tool
import json # For a more structured mock response

@tool
def web_search(query: str, num_results: int = 3) -> str:
    """
    Simulates performing a web search and returns a list of findings.
    In a real system, this would call a search API (Google, Bing, DuckDuckGo, etc.).

    Args:
        query (str): The search query.
        num_results (int): The number of simulated results to return.

    Returns:
        str: A JSON string representing a list of search results (title, snippet, url).
    """
    print(f"TOOL: Simulating web search for '{query}' (returning {num_results} results)...")
    mock_results = []
    for i in range(num_results):
        mock_results.append({
            "title": f"Simulated Result {i+1} for '{query}'",
            "snippet": f"This is a brief snippet about '{query}' from mock source {i+1}. It contains relevant keywords and information.",
            "url": f"http://example.com/search-result-{query.replace(' ', '-')}-{i+1}"
        })
    return json.dumps(mock_results)

@tool
def write_str_to_markdown(string_data: str, md_filename: str):
    """
    Writes a string to a Markdown (.md) file.

    This function takes a string (presumably Markdown formatted) and writes it to a file.
    If the file already exists, it will be overwritten with the new data.

    Args:
        string_data (str): The string containing the Markdown data to be written to the file.
        md_filename (str): The name of the Markdown file (e.g., 'blog_post.md').
    """
    # Write the string data to the text file
    with open(md_filename, mode='w', encoding='utf-8') as file:
        file.write(string_data)
    print(f"TOOL: Markdown data successfully written to {md_filename}")
    return f"Successfully wrote content to {md_filename}"

# --- Create the Crew ---
with Crew() as blog_crew:

    # --- Agent 1: Researcher ---
    researcher_agent = Agent(
        name="Tech Trend Researcher",
        backstory="You are an AI assistant specialized in identifying and summarizing current technology trends. You are adept at using web search tools to find relevant articles and synthesize information.",
        task_description="Research the latest advancements in 'Quantum Computing' for a general tech audience. Focus on breakthroughs in the last 6-12 months. Provide a summary of 3-5 key findings.",
        task_expected_output="A concise summary of 3-5 key findings, each with a brief explanation. Format as a list. Include sources if possible (from the search tool).",
        tools=[web_search] # Researcher uses the web_search tool
    )

    # --- Agent 2: Blog Post Writer ---
    blog_writer_agent = Agent(
        name="Engaging Tech Blogger",
        backstory="You are a skilled tech blogger known for writing clear, engaging, and informative articles for a non-expert audience. You take research findings and turn them into compelling narratives.",
        task_description="Write a blog post (approximately 500-700 words) based on the provided research about 'Quantum Computing'. The tone should be enthusiastic and slightly futuristic but grounded in the research. Explain complex concepts simply.",
        task_expected_output="A well-structured blog post with an introduction, several body paragraphs detailing the findings, and a conclusion. Use Markdown for formatting (headings, lists, bolding)."
    )

    # --- Agent 3: Title Generator ---
    title_agent = Agent(
        name="Catchy Title Creator",
        backstory="You are a marketing expert with a knack for crafting irresistible titles that grab attention and accurately reflect content.",
        task_description="Based on the provided blog post about 'Quantum Computing', generate 3-5 catchy and SEO-friendly title options.",
        task_expected_output="A list of 3-5 title suggestions, each on a new line."
    )

    # --- Agent 4: Social Media Summarizer ---
    social_media_agent = Agent(
        name="Social Media Whiz",
        backstory="You excel at distilling information into short, punchy updates suitable for platforms like Twitter/X or LinkedIn. You know how to use relevant hashtags.",
        task_description="Read the provided blog post and its chosen title. Create a concise summary (max 280 characters) suitable for a Twitter/X post to promote the blog post. Include 2-3 relevant hashtags.",
        task_expected_output="A single string, 280 characters or less, including hashtags. Example: 'Mind-blowing quantum leaps! Our new post dives into the latest quantum computing breakthroughs. Read more: [Link_Placeholder] #QuantumComputing #TechFuture'"
    )

    # --- Agent 5: Content Publisher ---
    publisher_agent = Agent(
        name="Digital Content Publisher",
        backstory="You are responsible for taking finalized content and publishing it to the correct digital channels. You are meticulous with file naming and organization.",
        task_description="You will receive a complete blog post (with title implicitly part of it or in context) and a social media summary. Save the full blog post content to a Markdown file named 'quantum_computing_blog_post.md'. The social media summary is for information but doesn't need to be saved by you in this task.",
        task_expected_output="Confirmation that the blog post has been saved to 'quantum_computing_blog_post.md'.",
        tools=[write_str_to_markdown] # Publisher uses the file writing tool
    )

    # --- Define Dependencies ---
    # Researcher -> Blog Writer
    # Blog Writer -> Title Generator
    # Blog Writer -> Social Media Summarizer (needs the full content)
    # Blog Writer -> Publisher (to save the post)
    # Title Generator -> Social Media Summarizer (social post might use the title) - Optional, but good for context
    # Title Generator -> Publisher (Publisher might want the title for context, though not strictly saving it separately)

    researcher_agent >> blog_writer_agent

    blog_writer_agent >> title_agent
    blog_writer_agent >> social_media_agent
    blog_writer_agent >> publisher_agent # Publisher gets the main blog content

    # Title agent's output could inform the social media agent and publisher
    title_agent >> social_media_agent # Social media agent gets context from title
    title_agent >> publisher_agent    # Publisher gets context from title

# --- Visualize and Run the Crew ---
print("--- Blog Post Generation Crew Workflow ---")
blog_crew.plot().render('blog_crew_workflow', view=True) # Saves and tries to open the plot

print("\n--- Running Blog Post Generation Crew ---")
blog_crew.run()

print("\n--- Crew Run Complete ---")
print("Check for 'quantum_computing_blog_post.md' in your current directory.")