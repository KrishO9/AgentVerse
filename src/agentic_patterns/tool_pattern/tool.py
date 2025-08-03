import json
from typing import Callable, get_origin, get_args, Union
import inspect


# def get_fn_signature(fn: Callable) -> dict:
#     """
#     Generates the signature for a given function.

#     Args:
#         fn (Callable): The function whose signature needs to be extracted.

#     Returns:
#         dict: A dictionary containing the function's name, description,
#               and parameter types.
#     """
#     fn_signature: dict = {
#         "name": fn.__name__,
#         "description": fn.__doc__,
#         "parameters": {"properties": {}},
#     }
#     schema = {
#         k: {"type": v.__name__} for k, v in fn.__annotations__.items() if k != "return"
#     }
#     fn_signature["parameters"]["properties"] = schema
#     return fn_signature

def get_type_name(type_hint: any) -> str:
    """
    Gets a user-friendly and schema-friendly name for a type hint.
    Handles simple types, generic types (like list[str]), and Union types (like str | None).
    """
    origin = get_origin(type_hint)
    args = get_args(type_hint) # Get args once

    if origin is None:  # Simple type like int, str, or a class
        if hasattr(type_hint, '__name__'):
            return type_hint.__name__
        else:
            return str(type_hint)
    elif origin is list: # Handles list (from type hints)
        return "list"
    elif origin is dict: # Handles dict (from type hints)
        return "object"
    # For Python 3.10+ (types.UnionType) and older (typing.Union)
    elif origin is Union or (hasattr(origin, '_is_union') and origin._is_union): # A more robust check for UnionType
        # For LLMs, if NoneType is one of the args, it often implies optional.
        # We can pick the first non-NoneType type.
        non_none_types = [arg for arg in args if arg is not type(None)]
        if len(non_none_types) == 1:
            return get_type_name(non_none_types[0])
        elif non_none_types:
            # If multiple non-None types, this simple model picks the first.
            # A full JSON schema might use "anyOf" with all non_none_types.
            return get_type_name(non_none_types[0]) 
        else: # Only NoneType, should not happen for parameters that are not just 'None'
            return "null" 
    else:
        # For other generic types, try to get the name of the origin.
        # This might be things like collections.abc.Callable, etc.
        if hasattr(origin, '__name__'):
            return origin.__name__.lower() # e.g. 'callable'
        return str(origin).lower() # Fallback, e.g. 'typing.callable'


# ... rest of your get_fn_signature function (it uses get_type_name correctly) ...
# Ensure get_fn_signature is also using get_origin and get_args correctly.
# The version I provided previously should be fine:

def get_fn_signature(fn: Callable) -> dict:
    """
    Generates the signature for a given function.
    """
    fn_signature: dict = {
        "name": fn.__name__,
        "description": fn.__doc__,
        "parameters": {"type": "object", "properties": {}, "required": []},
    }
    
    required_params = []
    properties_schema = {}
    sig = inspect.signature(fn)

    for param_name, param_obj in sig.parameters.items():
        if param_name == "return": # Should be checking fn.__annotations__ for return
            continue
        
        # Get annotation from fn.__annotations__ for the parameter
        v_annotation = fn.__annotations__.get(param_name)
        if v_annotation is None and param_obj.annotation is not inspect.Parameter.empty:
            v_annotation = param_obj.annotation # Fallback to signature's annotation if not in __annotations__
        elif v_annotation is None:
            # If no type hint, LLM might struggle. We can default to 'string' or skip.
            # For now, let's be explicit or skip if no type hint is found.
            # For this example, let's assume tools are type-hinted. If not, this would need a default.
            print(f"Warning: No type hint for parameter '{param_name}' in function '{fn.__name__}'. Skipping for schema.")
            continue


        type_name_for_schema = get_type_name(v_annotation)
        
        is_optional_by_default = (param_obj.default is not inspect.Parameter.empty)
        # Check if it's Optional[X] or X | None
        origin_type = get_origin(v_annotation)
        args_type = get_args(v_annotation)
        is_optional_by_type = (origin_type is Union and type(None) in args_type) or \
                              (hasattr(origin_type, '_is_union') and origin_type._is_union and type(None) in args_type)


        is_optional = is_optional_by_default or is_optional_by_type

        properties_schema[param_name] = {"type": type_name_for_schema}
        
        # Parameter description from docstring (basic parsing)
        if fn.__doc__:
            doc_lines = fn.__doc__.split('\n')
            for line in doc_lines:
                line = line.strip()
                # Improved regex for more flexible parsing:
                # Looks for "param_name:" or "param_name (type):"
                import re
                match = re.match(rf"{re.escape(param_name)}\s*(?:\(.*\))?:\s*(.+)", line)
                if match:
                    properties_schema[param_name]["description"] = match.group(1).strip()
                    break
        
        if not is_optional:
            required_params.append(param_name)

    # Ensure all annotated parameters are in properties_schema
    for k_annot, v_annot in fn.__annotations__.items():
        if k_annot != "return" and k_annot not in properties_schema and k_annot in sig.parameters:
            # This handles cases where a param was in __annotations__ but might have been missed
            # by iterating sig.parameters if its annotation was complex and caused an early skip (now fixed)
            param_obj = sig.parameters[k_annot]
            type_name_for_schema = get_type_name(v_annot)
            is_optional_by_default = (param_obj.default is not inspect.Parameter.empty)
            origin_type = get_origin(v_annot)
            args_type = get_args(v_annot)
            is_optional_by_type = (origin_type is Union and type(None) in args_type) or \
                                  (hasattr(origin_type, '_is_union') and origin_type._is_union and type(None) in args_type)
            is_optional = is_optional_by_default or is_optional_by_type

            properties_schema[k_annot] = {"type": type_name_for_schema}
            # Add description parsing here too if needed for these cases
            if not is_optional:
                 if k_annot not in required_params: # Avoid duplicates
                    required_params.append(k_annot)


    fn_signature["parameters"]["properties"] = properties_schema
    if required_params:
        fn_signature["parameters"]["required"] = required_params
    
    return fn_signature


def validate_arguments(tool_call: dict, tool_signature: dict) -> dict:
    properties = tool_signature["parameters"]["properties"]

    # Expanded type mapping and handling
    type_mapping = {
        "integer": int, # Common JSON schema type for int
        "int": int,
        "string": str, # Common JSON schema type for str
        "str": str,
        "boolean": bool, # Common JSON schema type for bool
        "bool": bool,
        "number": float, # Common JSON schema type for float/number
        "float": float,
        "array": list, # Common JSON schema type for list
        "list": list,
        "object": dict, # Common JSON schema type for dict
        # 'null' can be used for None, but often handled by 'required' field
    }

    args_to_convert = tool_call.get("arguments", {})
    converted_args = {}

    for arg_name, arg_value in args_to_convert.items():
        if arg_name not in properties:
            print(f"Warning: Argument '{arg_name}' provided by LLM but not in tool signature. Skipping.")
            converted_args[arg_name] = arg_value # Keep it as is or discard
            continue

        expected_schema_type = properties[arg_name].get("type")
        python_type = type_mapping.get(expected_schema_type.lower()) # .lower() for case-insensitivity

        if arg_value is None: # If LLM explicitly passes null/None
            # Check if parameter is optional (not in 'required' list or allows null)
            if arg_name not in tool_signature["parameters"].get("required", []) or "null" in properties[arg_name].get("type", []): # More robust check for null in type
                converted_args[arg_name] = None
                continue
            else:
                # This case is tricky: LLM sent null for a required non-nullable field.
                # Decide on error handling. For now, let it pass and potentially fail in tool.run()
                print(f"Warning: LLM provided null for required argument '{arg_name}'.")
                converted_args[arg_name] = None # Or raise error
                continue


        if python_type:
            if not isinstance(arg_value, python_type):
                try:
                    converted_args[arg_name] = python_type(arg_value)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not convert argument '{arg_name}' value '{arg_value}' to type '{expected_schema_type}'. Error: {e}. Using original value.")
                    converted_args[arg_name] = arg_value # Fallback to original value
            else:
                converted_args[arg_name] = arg_value # Already correct type
        else:
            print(f"Warning: Unknown expected type '{expected_schema_type}' for argument '{arg_name}'. Using original value.")
            converted_args[arg_name] = arg_value # Fallback

    tool_call["arguments"] = converted_args
    return tool_call

# def validate_arguments(tool_call: dict, tool_signature: dict) -> dict:
#     """
#     Validates and converts arguments in the input dictionary to match the expected types.

#     Args:
#         tool_call (dict): A dictionary containing the arguments passed to the tool.
#         tool_signature (dict): The expected function signature and parameter types.

#     Returns:
#         dict: The tool call dictionary with the arguments converted to the correct types if necessary.
#     """
#     properties = tool_signature["parameters"]["properties"]

#     # TODO: This is overly simplified but enough for simple Tools.
#     type_mapping = {
#         "int": int,
#         "str": str,
#         "bool": bool,
#         "float": float,
#     }

#     for arg_name, arg_value in tool_call["arguments"].items():
#         expected_type = properties[arg_name].get("type")

#         if not isinstance(arg_value, type_mapping[expected_type]):
#             tool_call["arguments"][arg_name] = type_mapping[expected_type](arg_value)

#     return tool_call


class Tool:
    """
    A class representing a tool that wraps a callable and its signature.

    Attributes:
        name (str): The name of the tool (function).
        fn (Callable): The function that the tool represents.
        fn_signature (str): JSON string representation of the function's signature.
    """

    def __init__(self, name: str, fn: Callable, fn_signature: str):
        self.name = name
        self.fn = fn
        self.fn_signature = fn_signature

    def __str__(self):
        return self.fn_signature

    def run(self, **kwargs):
        """
        Executes the tool (function) with provided arguments.

        Args:
            **kwargs: Keyword arguments passed to the function.

        Returns:
            The result of the function call.
        """
        return self.fn(**kwargs)


# def tool(fn: Callable):
#     """
#     A decorator that wraps a function into a Tool object.

#     Args:
#         fn (Callable): The function to be wrapped.

#     Returns:
#         Tool: A Tool object containing the function, its name, and its signature.
#     """

#     def wrapper():
#         fn_signature = get_fn_signature(fn)
#         return Tool(
#             name=fn_signature.get("name"), fn=fn, fn_signature=json.dumps(fn_signature)
#         )

#     return wrapper()

def tool(fn: Callable): # This part of the decorator is fine as it was in your last good version
    """
    A decorator that wraps a function into a Tool object.

    Args:
        fn (Callable): The function to be wrapped.

    Returns:
        Tool: A Tool object containing the function, its name, and its signature.
    """
    # This was the version you had that created the Tool instance immediately
    # which is needed for the Agent class to receive a Tool object directly.
    fn_signature_dict = get_fn_signature(fn)
    return Tool(
        name=fn_signature_dict.get("name"),
        fn=fn,
        fn_signature=json.dumps(fn_signature_dict)
    )
