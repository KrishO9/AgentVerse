from dotenv import load_dotenv
from groq import Groq
from colorama import Fore

from ..utils.completions import completions_create
from ..utils.completions import build_prompt_structure

from ..utils.completions import FixedFirstChatHistory
from ..utils.logging import fancy_print
from ..utils.logging import fancy_step_tracker


from ..utils.completions import update_chat_history





load_dotenv()

BASE_GENERATION_SYSTEM_PROMPT = """
Your task is to Generate the best content possible for the user's request.
If the user provides critique, respond with a revised version of your previous attempt.
You must always output the revised content.
"""

BASE_REFLECTION_SYSTEM_PROMPT = """
You are tasked with generating critique and recommendations to the user's generated content.
If the user content has something wrong or something to be improved, output a list of recommendations
and critiques. If the user content is ok and there's nothing to change, output this: <OK>
"""

class Reflection_Agent:
    """
    A class that implements a Reflection Agent, which generates responses and reflects
    on them using the LLM to iteratively improve the interaction.
    Attributes:
        model (str): The model name used for generating and reflecting on responses.
        client (Groq): An instance of the Groq client to interact with the language model.
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        self.client=Groq()
        self.model = model

    def _request_completion(
            self,
            history:list,
            verbose:int=0,
            log_title: str = "COMPLETION",
            log_color : str = "",
    ):
        """
        A private method to request a completion from the Groq model.

        Args:
            history (list): A list of messages forming the conversation or reflection history.
            verbose (int, optional): The verbosity level. Defaults to 0 (no output).

        Returns:
            str: The model-generated response.
        """

        output = completions_create(self.client, history,self.model)

        if verbose>0:
            print(log_color, f"\n\n{log_title}\n\n", output)

        return output

    def generate(self, generation_history: list, verbose:int=0) -> str:

        return self._request_completion(
            generation_history, verbose, log_title="GENERATION", log_color=Fore.BLUE
        )
    
    def reflect(self, reflection_history: list, verbose: int = 0) -> str:
        return self._request_completion(
            reflection_history,verbose, log_title="REFLECTION", log_color=Fore.GREEN
        ) 

    def run(
            self,
            user_msg: str,
            generation_system_prompt: str= "",
            reflection_system_prompt: str= "",
            n_steps: int = 4,
            verbose: int = 0,
    ) -> str:
        generation_system_prompt += BASE_GENERATION_SYSTEM_PROMPT
        reflection_system_prompt += BASE_REFLECTION_SYSTEM_PROMPT

        generation_history = FixedFirstChatHistory(
            [
                build_prompt_structure(generation_system_prompt,role="system"),
                build_prompt_structure(user_msg, role="user"),
            ],total_length=3
        )

        reflection_history = FixedFirstChatHistory(
            [
                build_prompt_structure(reflection_system_prompt, role="system"),
            ],total_length=3
        )

        for step in range(n_steps):
            if verbose > 0:
                fancy_step_tracker(step, n_steps)


            # GENERATE THE RESPONSE
            generation = self.generate(generation_history,verbose=verbose)
            update_chat_history(generation_history,generation,"assistant")
            update_chat_history(reflection_history,generation, "user")

            # REFLECT and CRITIQUE the generation
            critique = self.reflect(reflection_history, verbose=verbose)

            if "<OK>" in critique:
                print(
                    Fore.RED,
                    "\n\n STOP SEQUENCE FOUND..stopping reflection loop \n\n",
                ) 
                break
                
            update_chat_history(generation_history,critique,"user")
            update_chat_history(reflection_history,critique,"assistant")
        
        return generation


        