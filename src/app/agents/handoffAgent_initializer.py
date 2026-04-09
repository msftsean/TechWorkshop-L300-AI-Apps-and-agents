import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    PromptAgentDefinitionTextOptions,
    TextResponseFormatJsonSchema
) 
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from services.handoff_service import IntentClassification

load_dotenv()

HANDOFF_AGENT_PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'prompts', 'HandoffAgentPrompt.txt')
with open(HANDOFF_AGENT_PROMPT_PATH, 'r', encoding='utf-8') as file:
    HANDOFF_AGENT_PROMPT = file.read()

project_endpoint = os.environ["FOUNDRY_ENDPOINT"]

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)

project_client=project_client
model=os.environ["gpt_deployment"]
name="handoff-service"
description="Zava Handoff Service Agent"
instructions=HANDOFF_AGENT_PROMPT

definition = PromptAgentDefinition(
    model=model,
    text=PromptAgentDefinitionTextOptions(
        format=TextResponseFormatJsonSchema(
            name="IntentClassification", schema=IntentClassification.model_json_schema()
        )
    ),
    instructions=instructions
)

with project_client:
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
