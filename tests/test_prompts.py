"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_V2_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_V2_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_v2():
    data = load_prompts(PROMPT_V2_PATH)
    return data[PROMPT_V2_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_v2):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_v2
        assert prompt_v2["system_prompt"].strip()

    def test_prompt_has_role_definition(self, prompt_v2):
        """Verifica se o prompt define uma persona (ex: Product Manager)."""
        system_prompt = prompt_v2["system_prompt"].lower()
        assert "product manager" in system_prompt

    def test_prompt_mentions_format(self, prompt_v2):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_v2["system_prompt"].lower()
        assert "markdown" in system_prompt
        assert "como" in system_prompt
        assert "eu quero" in system_prompt
        assert "para que" in system_prompt

    def test_prompt_has_few_shot_examples(self, prompt_v2):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_v2["system_prompt"].lower()
        assert "exemplo" in system_prompt
        assert "entrada:" in system_prompt
        assert "saída:" in system_prompt

    def test_prompt_no_todos(self, prompt_v2):
        """Garante que você não esqueceu nenhum [TODO] no texto."""
        full_text = prompt_v2["system_prompt"] + prompt_v2.get("user_prompt", "")
        assert "[TODO]" not in full_text

    def test_minimum_techniques(self, prompt_v2):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_v2.get("techniques_applied", [])
        assert len(techniques) >= 2

    def test_validate_prompt_structure(self, prompt_v2):
        """Valida estrutura mínima exigida pelo utilitário do projeto."""
        is_valid, errors = validate_prompt_structure(prompt_v2)
        assert is_valid, f"Erros de estrutura: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
