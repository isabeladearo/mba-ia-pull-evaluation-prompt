"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"
HUB_REPO_NAME = "bug_to_user_story_v2"


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    is_valid, structure_errors = validate_prompt_structure(prompt_data)
    errors.extend(structure_errors)

    user_prompt = prompt_data.get("user_prompt", "").strip()
    if not user_prompt:
        errors.append("user_prompt está vazio")

    if "{bug_report}" not in user_prompt:
        errors.append("user_prompt deve conter a variável {bug_report}")

    return (len(errors) == 0, errors)


def _yaml_to_chat_prompt(prompt_data: dict) -> ChatPromptTemplate:
    """Converte dados do YAML em ChatPromptTemplate para o LangSmith Hub."""
    return ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("human", prompt_data["user_prompt"]),
    ])


def _build_readme(prompt_data: dict, hub_name: str) -> str:
    """Gera README do prompt no Hub com metadados do desafio."""
    techniques = prompt_data.get("techniques_applied", [])
    tags = prompt_data.get("tags", [])

    techniques_list = "\n".join(f"- {technique}" for technique in techniques)
    tags_list = ", ".join(tags)

    return f"""# {hub_name}

{prompt_data.get("description", "")}

## Versão
{prompt_data.get("version", "v2")}

## Técnicas aplicadas
{techniques_list}

## Tags
{tags_list}

## Objetivo
Converter relatos de bugs em User Stories ágeis com critérios de aceitação em Markdown.
"""


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome completo no Hub (owner/repo)
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        prompt_template = _yaml_to_chat_prompt(prompt_data)
        readme = _build_readme(prompt_data, prompt_name)
        tags = prompt_data.get("tags", [])

        print(f"Publicando prompt: {prompt_name}")
        print(f"   Tags: {', '.join(tags)}")
        print(f"   Técnicas: {', '.join(prompt_data.get('techniques_applied', []))}")

        url = hub.push(
            prompt_name,
            prompt_template,
            new_repo_is_public=True,
            new_repo_description=prompt_data.get("description", ""),
            readme=readme,
            tags=tags,
        )

        print(f"✅ Prompt publicado com sucesso!")
        print(f"   URL: {url}")
        print(f"   Variáveis de entrada: {prompt_template.input_variables}")
        return True

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Erro ao fazer push do prompt: {e}")

        if "LangChain Hub handle" in error_msg or "public prompt" in error_msg:
            print("\n⚠️  Para publicar prompts PÚBLICOS, você precisa criar um handle no LangSmith:")
            print("   1. Acesse https://smith.langchain.com/prompts")
            print("   2. Crie seu handle (nome de usuário público no Hub)")
            print("   3. Atualize USERNAME_LANGSMITH_HUB no .env com esse handle")
            print("   4. Rode novamente: python src/push_prompts.py")
        elif "another tenant" in error_msg or "Requested tenant" in error_msg:
            print("\n⚠️  O USERNAME_LANGSMITH_HUB não corresponde à sua conta LangSmith.")
            print("   1. Abra https://smith.langchain.com/prompts")
            print("   2. Verifique seu handle (ícone de cadeado em qualquer prompt seu)")
            print("   3. Atualize USERNAME_LANGSMITH_HUB no .env")
            print("   4. Rode novamente: python src/push_prompts.py")
        else:
            print("\nVerifique:")
            print("  - LANGSMITH_API_KEY no .env")
            print("  - USERNAME_LANGSMITH_HUB no .env")
            print("  - Permissão para criar prompts no LangSmith")

        return False


def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]

    if not check_env_vars(required_vars):
        return 1

    print_section_header("Push de prompt otimizado para o LangSmith Hub")

    yaml_data = load_yaml(str(INPUT_PATH))
    if not yaml_data or PROMPT_KEY not in yaml_data:
        print(f"❌ Arquivo não encontrado ou chave ausente: {INPUT_PATH}")
        return 1

    prompt_data = yaml_data[PROMPT_KEY]

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido. Corrija os problemas antes do push:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✅ Validação local concluída")

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    hub_name = f"{username}/{HUB_REPO_NAME}"

    success = push_prompt_to_langsmith(hub_name, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
