from agentic_patterns.planning_pattern.react_agent import ReactAgent
import math
import os
import re
import json
from agentic_patterns.tool_pattern.tool import tool
from agentic_patterns.utils.extraction import extract_tag_content

@tool
def sum_two_elements(a: int, b: int) -> int:
    """
    Computes the sum of two integers.

    Args:
        a (int): The first integer to be summed.
        b (int): The second integer to be summed.

    Returns:
        int: The sum of `a` and `b`.
    """
    return a + b


@tool
def multiply_two_elements(a: int, b: int) -> int:
    """
    Multiplies two integers.

    Args:
        a (int): The first integer to multiply.
        b (int): The second integer to multiply.

    Returns:
        int: The product of `a` and `b`.
    """
    return a * b

@tool
def compute_log(x: int) -> float | str:
    """
    Computes the logarithm of an integer `x` with an optional base.

    Args:
        x (int): The integer value for which the logarithm is computed. Must be greater than 0.

    Returns:
        float: The logarithm of `x` to the specified `base`.
    """
    if x <= 0:
        return "Logarithm is undefined for values less than or equal to 0."
    
    return math.log(x)


available_tools = {
    "sum_two_elements": sum_two_elements,
    "multiply_two_elements": multiply_two_elements,
    "compute_log": compute_log
}

agent = ReactAgent(tools=[sum_two_elements, multiply_two_elements, compute_log])

agent.run(user_msg="I want to calculate the sum of 1234 and 5678 and multiply the result by 5. Then, I want to take the logarithm of this result")