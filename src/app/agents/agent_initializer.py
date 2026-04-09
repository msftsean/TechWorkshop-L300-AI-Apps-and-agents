from typing import List, Any
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.core.exceptions import ResourceNotFoundError
from dotenv import load_dotenv

load_dotenv()

def initialize_agent(project_client : AIProjectClient, model : str, name : str, description : str, instructions : str, tools : List[Any]):
    with project_client:
        definition = PromptAgentDefinition(
            model=model,
            instructions=instructions,
            tools=tools
        )
        try:
            agent = project_client.agents.create_version(
                agent_name=name,
                description=description,
                definition=definition
            )
        except ResourceNotFoundError:
            project_client.agents._create_agent(
                name=name,
                description=description,
                definition=definition
            )
            agent = project_client.agents.create_version(
                agent_name=name,
                description=description,
                definition=definition
            )
        print(f"Created {name} agent, ID: {agent.id}")
