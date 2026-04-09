# Azure imports
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.evaluation.red_team import RedTeam, RiskCategory, AttackStrategy
from pyrit.prompt_target import OpenAIChatTarget
import httpx
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

# Azure AI Project Information
azure_ai_project = os.getenv("FOUNDRY_ENDPOINT")

# Red Team Agent with custom attack prompts
red_team_agent = RedTeam(
    azure_ai_project=azure_ai_project,
    credential=DefaultAzureCredential(),
    custom_attack_seed_prompts="data/custom_attack_prompts.json",
)

# Configuration for Azure OpenAI model using managed identity
credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(credential, "https://ai.azure.com/.default")

gpt_endpoint = os.environ.get("gpt_endpoint").rstrip("/")

chat_target = OpenAIChatTarget(
    model_name=os.environ.get("gpt_deployment"),
    endpoint=f"{gpt_endpoint}/openai/v1/",
    api_key=token_provider,
)

# Custom target for Cora agent
foundry_endpoint = os.getenv("FOUNDRY_ENDPOINT")


def cora_target(query: str) -> str:
    """Send a query to the Cora agent via the Foundry API."""
    token = credential.get_token("https://ai.azure.com/.default").token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [{"role": "user", "content": query}],
    }
    response = httpx.post(
        f"{foundry_endpoint}/agents/cora/runs?api-version=2025-11-15-preview",
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")


async def main():
    red_team_result = await red_team_agent.scan(
        target=cora_target,
        scan_name="Red Team Scan - Easy-Moderate Strategies",
        attack_strategies=[
            AttackStrategy.Flip,
            AttackStrategy.ROT13,
            AttackStrategy.Base64,
            AttackStrategy.AnsiAttack,
            AttackStrategy.Tense
        ])

asyncio.run(main())
