from textwrap import dedent
from agentic_patterns.tool_pattern.tool import Tool
from agentic_patterns.planning_pattern.react_agent import ReactAgent

from agentic_patterns.multiagent_pattern.crew import Crew


class Agent:
        """
    Represents an AI agent that can work as part of a team to complete tasks.

    This class implements an agent with dependencies, context handling, and task execution capabilities.
    It can be used in a multi-agent system where agents collaborate to solve complex problems.

    Attributes:
        name (str): The name of the agent.
        backstory (str): The backstory or background of the agent.
        task_description (str): A description of the task assigned to the agent.
        task_expected_output (str): The expected format or content of the task output.
        react_agent (ReactAgent): An instance of ReactAgent used for generating responses.
        dependencies (list[Agent]): A list of Agent instances that this agent depends on.
        dependents (list[Agent]): A list of Agent instances that depend on this agent.
        context (str): Accumulated context information from other agents.

    Args:
        name (str): The name of the agent.
        backstory (str): The backstory or background of the agent.
        task_description (str): A description of the task assigned to the agent.
        task_expected_output (str, optional): The expected format or content of the task output. Defaults to "".
        tools (list[Tool] | None, optional): A list of Tool instances available to the agent. Defaults to None.
        llm (str, optional): The name of the language model to use. Defaults to "llama-3.3-70b-versatile".
    """
        def __init__(
            self,
            name: str,
            backstory: str,
            task_description : str,
            task_expected_output: str = "",
            tools: list[Tool] | None = None,
            llm: str = "llama-3.3-70b-versatile",
        ):
                self.name = name
                self.backstory = backstory
                self.task_description = task_description
                self.task_expected_output = task_expected_output
                self.react_agent = ReactAgent(tools = tools or [], model = llm, system_prompt=backstory)
                self.dependencies: list[Agent] = []
                self.dependents: list[Agent] = []

                self.context = ""

                #Automatically register this agent to the active crew context if one exists
                Crew.register_agent(self)

        
        def __repr__(self):
                return f"{self.name}"
        
        def __rshift__(self,other):
                ''' A(self) >> B(other) 
                '''
                self.add_dependent(other)
                return other
        
        def __lshift__(self,other):
                """ A(self) << B(other)"""
                self.add_dependency(other)
                return other
        
        def __rrshift__(self, other):
                ''' A(other) >> B(self)'''
                self.add_dependency(other)
                return self
        def __rlshift__(self,other):
                ''' A(other) << B(self)'''
                self.add_dependent(other)
                return self

        def add_dependency(self, other):
                
                if isinstance(other,Agent):
                        self.dependencies.append(other)
                        other.dependents.append(self)
                elif isinstance(other,list) and all(isinstance(item,Agent) for item in other):
                        for item in other:
                                self.dependencies.append(other)
                                item.dependents.append(self)
                else:
                        raise TypeError("The dependency must be an instance or list of Agent")

        def add_dependent(self,other):

                if isinstance(other,Agent):
                        other.dependencies.append(self)
                        self.dependents.append(other)
                elif isinstance(other,list) and all(isinstance(item,Agent) for item in other):
                        for item in other:
                                item.dependencies.append(self)
                                self.dependents.append(item)
                else:
                    raise TypeError("The dependent must be an instance or list of Agent.")

        def recieve_context(self, input_data):
                self.context += f"{self.name} recieved context: \n {input_data}"

        def create_prompt(self):
            prompt = dedent(
                f"""
            You are an AI agent. You are part of a team of agents working together to complete a task.
            I'm going to give you the task description enclosed in <task_description></task_description> tags. I'll also give
            you the available context from the other agents in <context></context> tags. If the context
            is not available, the <context></context> tags will be empty. You'll also receive the task
            expected output enclosed in <task_expected_output></task_expected_output> tags. With all this information
            you need to create the best possible response, always respecting the format as describe in
            <task_expected_output></task_expected_output> tags. If expected output is not available, just create
            a meaningful response to complete the task.

            <task_description>
            {self.task_description}
            </task_description>

            <task_expected_output>
            {self.task_expected_output}
            </task_expected_output>

            <context>
            {self.context}
            </context>

            Your response:
            """
            ).strip()

            return prompt
        
        def run(self):
                msg = self.create_prompt()
                output = self.react_agent.run(user_msg=msg)

                for dependent in self.dependents:
                        dependent.recieve_context(output)
                return output


        