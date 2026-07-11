"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "prompts" / "bug_to_user_story_v1.yml"
PROMPT_HUB_NAME = "leonanluppi/bug_to_user_story_v1"
PROMPT_KEY = "bug_to_user_story_v1"


def _extract_prompt_texts(prompt_template: ChatPromptTemplate) -> tuple[str, str]:
    """Extrai system_prompt e user_prompt de um ChatPromptTemplate."""
    system_prompt = ""
    user_prompt = ""

    for message in prompt_template.messages:
        if not hasattr(message, "prompt"):
            continue

        template_text = message.prompt.template
        message_type = type(message).__name__

        if "System" in message_type:
            system_prompt = template_text
        elif "Human" in message_type:
            user_prompt = template_text

    return system_prompt, user_prompt


def _chat_prompt_to_yaml(prompt_template: ChatPromptTemplate) -> dict:
    """Converte ChatPromptTemplate do Hub para estrutura YAML do projeto."""
    system_prompt, user_prompt = _extract_prompt_texts(prompt_template)
    metadata = prompt_template.metadata or {}

    owner = metadata.get("lc_hub_owner", "leonanluppi")
    repo = metadata.get("lc_hub_repo", "bug_to_user_story_v1")

    return {
        PROMPT_KEY: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "source_hub": f"{owner}/{repo}",
            "commit_hash": metadata.get("lc_hub_commit_hash"),
            "tags": ["bug-analysis", "user-story", "product-management"],
            "techniques_applied": [],
        }
    }


def pull_prompts_from_langsmith() -> bool:
    """
    Faz pull do prompt v1 do LangSmith Hub e salva localmente.

    Returns:
        True se sucesso, False caso contrário
    """
    print_section_header(f"Pull do LangSmith Hub: {PROMPT_HUB_NAME}")

    try:
        print(f"Conectando ao LangSmith e baixando prompt...")
        prompt_template = hub.pull(PROMPT_HUB_NAME)

        if not isinstance(prompt_template, ChatPromptTemplate):
            print(f"❌ Tipo inesperado retornado pelo Hub: {type(prompt_template)}")
            return False

        prompt_data = _chat_prompt_to_yaml(prompt_template)

        if not prompt_data[PROMPT_KEY]["system_prompt"]:
            print("❌ system_prompt vazio após pull")
            return False

        if save_yaml(prompt_data, str(OUTPUT_PATH)):
            print(f"✅ Prompt salvo em: {OUTPUT_PATH}")
            print(f"   Variáveis de entrada: {prompt_template.input_variables}")
            return True

        return False

    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        print("\nVerifique:")
        print("  - LANGSMITH_API_KEY no .env")
        print("  - Conexão com a internet")
        print(f"  - Prompt público disponível: {PROMPT_HUB_NAME}")
        return False


def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY"]

    if not check_env_vars(required_vars):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
