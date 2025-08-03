# AgentVerse : Agentic Framework build from scratch in Python

*Making AI agents work together like a well-oiled comedy team!*

Ever wanted to build AI agents that can collaborate, think, reflect, and use tools? This framework makes it as easy as `agent1 >> agent2 >> agent3` (literally!).


## 🏗️ The Magic Behind the Scenes

#### 1. **Multi-Agent Pattern** - *The Team Builder*
Chain agents together like dominoes:
```python
researcher >> writer >> editor >> publisher
# Data flows automatically from one to the next!
```

#### 2. **ReAct Pattern** - *The Thinker*
Agents that think out loud:
```
<thought>I should search for this info</thought>
<action>searches the web</action>
<observation>found some results</observation>
<response>Here's what I learned...</response>
```

#### 3. **Reflection Pattern** - *The Self-Critic*
Agents that improve themselves:
```python
agent.run("Write a poem", n_steps=3)
# Step 1: writes poem
# Step 2: critiques and rewrites
# Step 3: polishes final version
```

#### 4. **Tool Pattern** - *The Handyperson*
Just add `@tool` and your function becomes agent-ready:
```python
@tool
def search_web(query: str) -> str:
    """Search the internet for information."""
    return "Found some cool stuff!"
```


## 🎪 Cool Examples (Yes, They Actually Work!)

### 🤣 **U.N. Comedy Clash** 
World leaders roasting each other! Modi, Trump, and Sharif take turns delivering diplomatic burns while an AI roastmaster keeps score.

### 📝 **Blog Content Factory**
Research → Write → Edit → Publish. A complete content pipeline that goes from "I need a blog post about quantum computing" to a finished article.

### ✈️ **Travel Buddy**
Tell it you want to visit Japan, and it creates a day-by-day itinerary with activities, hotels, and transport tips.

### 🎭 **Comedy Roast Machine**
Multiple AI comedians (the pun specialist, the observational comic, the one-liner expert) team up to roast anyone you want.

## 🎯 What Makes This Special?

### 🔗 **Chain Agents Like LEGO**
```python
agent1 >> agent2 >> agent3  # That's it! They're connected!
```

### 🧹 **Auto-Cleanup**
```python
with Crew() as team:
    # Make agents here
    pass  # Everything cleans up automatically
```

### 🎯 **Smart Type Handling**
Throw any Python types at it - `str | None`, `list[int]`, whatever. It just works.

### 📋 **No Manual Schemas**
Write a function, add `@tool`, and boom - the AI knows how to use it.

## 🛠️ Setup

### Install the Basics
```bash
pip install groq python-dotenv colorama graphviz tavily-python
```

### Get API Keys
```bash
export GROQ_API_KEY="your_key_here"
export TAVILY_API_KEY="your_key_here"  # Optional, for web search
```

### Requirements
- Python 3.10+ 
- Internet connection
- A sense of humor (optional but recommended)

## 🚀 Quick Start

### 1. Make Some Agents
```python
from agentic_patterns.multiagent_pattern import Agent, Crew

with Crew() as crew:
    researcher = Agent(
        name="Sherlock",
        backstory="I find things on the internet",
        task_description="Research whatever the user asks about"
    )
    
    writer = Agent(
        name="Shakespeare", 
        backstory="I make words sound fancy",
        task_description="Turn research into readable content"
    )
    
    researcher >> writer  # Sherlock feeds Shakespeare
    crew.run()  # Magic happens!
```

### 2. Make a Tool
```python
@tool
def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"It's sunny in {city}!"
```

### 3. Self-Improving Agent
```python
agent = Reflection_Agent()
result = agent.run("Write a haiku about cats", n_steps=3)
# It writes, critiques itself, and rewrites until it's perfect
```


## 🗂️ What's in the Box?

```
src/
├── agentic_patterns/      # The main framework
│   ├── multiagent_pattern/    # Team building
│   ├── planning_pattern/      # Thinking agents  
│   ├── reflection_pattern/    # Self-improving agents
│   └── tool_pattern/          # Tool integration
├── global.py             # UN Comedy roast battle
├── socio.py              # Blog writing pipeline
├── travel.py             # Trip planner
└── comic.py              # Comedy roast generator
```
