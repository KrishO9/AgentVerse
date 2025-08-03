from agentic_patterns.reflection_pattern import ReflectionAgent

agent = ReflectionAgent()

generation_system_prompt = "You are a Python programmer tasked with generating high quality Python code"

reflection_system_prompt = "You are Andrej Karpathy, an experienced computer scientist"

user_msg = "Generate a Python implementation of the Merge Sort algorithm"

final_response = agent.run(
    user_msg=user_msg,
    generation_system_prompt=generation_system_prompt,
    reflection_system_prompt=reflection_system_prompt,
    n_steps=4,
    verbose=1,
)

print(final_response)