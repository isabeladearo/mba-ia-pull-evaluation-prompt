# AGENTS.md — Contexto para agentes de IA

> Arquivo destinado a agentes (Cursor, Copilot, Claude Code, etc.) que forem dar manutenção neste repositório.
> Para instruções de execução humanas, consulte o [README.md](./README.md).

---

## Propósito

Projeto de **Pull, Otimização e Avaliação de Prompts** para desafio acadêmico (MBA IA — Full Cycle).

- **Não é uma API web** — é um pipeline CLI com 4 scripts Python + 1 arquivo YAML de prompt.
- Compartilham configuração via `.env` e integram com LangSmith Hub + OpenAI/Gemini.
- Objetivo: converter bug reports em user stories ágeis com métricas ≥ 0.8 em todas as 5 dimensões.

---

## Fluxo de dados

```
Pull:
  LangSmith Hub (leonanluppi/bug_to_user_story_v1) → pull_prompts.py → prompts/bug_to_user_story_v1.yml

Otimização:
  prompts/bug_to_user_story_v1.yml → (manual) → prompts/bug_to_user_story_v2.yml

Push:
  prompts/bug_to_user_story_v2.yml → push_prompts.py → LangSmith Hub ({username}/bug_to_user_story_v2)

Avaliação:
  Hub pull v2 + datasets/bug_to_user_story.jsonl → evaluate.py → metrics.py (LLM-as-Judge) → scores
```

---

## Arquivos principais

| Arquivo | Responsabilidade | Alterar? |
|---------|------------------|----------|
| `src/pull_prompts.py` | Pull de `leonanluppi/bug_to_user_story_v1` | Implementado — evitar mudanças desnecessárias |
| `src/push_prompts.py` | Push de `{username}/bug_to_user_story_v2` | Implementado — evitar mudanças desnecessárias |
| `src/evaluate.py` | Avaliação contra dataset de 15 exemplos | **NÃO alterar** (fornecido pelo desafio) |
| `src/metrics.py` | 5 métricas: F1, Clarity, Precision + derivadas | **NÃO alterar** (fornecido pelo desafio) |
| `src/utils.py` | LLM factory, YAML, validação | **NÃO alterar** (fornecido pelo desafio) |
| `prompts/bug_to_user_story_v2.yml` | Prompt otimizado — **principal artefato** | Sim, para iterar métricas |
| `datasets/bug_to_user_story.jsonl` | 15 bugs com ground truth | **NÃO alterar** (fornecido pelo desafio) |
| `tests/test_prompts.py` | 7 testes pytest da estrutura do prompt | Implementado — manter os 6 obrigatórios |
| `.env` | Credenciais (não commitar) | Sim |
| `.env.example` | Template sem chaves | Sim |

---

## Regras de negócio do prompt v2

### Formato de saída por complexidade

| Nível | Quando usar | Template |
|-------|-------------|----------|
| SIMPLES | Bug isolado de UI/validação, sem logs/endpoints | User story + Critérios de Aceitação |
| MÉDIO | Um problema com detalhes técnicos, performance, segurança | + Contexto Técnico + seções opcionais (Exemplo de Cálculo, Critérios de Prevenção) |
| COMPLEXO | 3+ problemas distintos numerados com IMPACTO/PROBLEMAS | Template `=== SEÇÕES ===` com critérios A/B/C/D + Tasks |

### Persona — regras críticas para F1/Correctness

- Cliente/UI → "Como um cliente...", "Como um usuário de iOS..."
- Admin/dashboard → "Como um administrador..."
- CRM/pipeline → "Como um vendedor gerenciando oportunidades no pipeline..."
- Lógica interna/webhook/estoque → "Como o sistema de e-commerce" ou "Como o sistema"
- Performance mobile → "Como um usuário do app Android/iOS..."

### Armadilhas conhecidas

1. **`TODO` no system_prompt** — `utils.validate_prompt_structure` rejeita qualquer ocorrência da substring `TODO` (inclui palavras como `TODOS`). Evitar.
2. **Classificar bug médio como COMPLEXO** — degrada F1 porque o formato `===` não bate com a referência do dataset.
3. **Persona errada** — ex.: bug de pipeline CRM com persona "cliente" em vez de "vendedor".
4. **Inventar detalhes** — penaliza Precision; usar só informações do relato.
5. **Hub handle** — push público exige handle criado em https://smith.langchain.com/prompts.

---

## Variáveis de ambiente (`.env`)

| Variável | Obrigatória | Default | Descrição |
|----------|-------------|---------|-----------|
| `LANGSMITH_API_KEY` | Sim | — | Chave do LangSmith |
| `USERNAME_LANGSMITH_HUB` | Sim (push/eval) | — | Handle público no Hub |
| `LANGSMITH_PROJECT` | Não | (nome no `.env`) | Projeto de tracing — use um nome **seu** no `.env` |
| `OPENAI_API_KEY` | Sim (se openai) | — | Chave OpenAI |
| `LLM_PROVIDER` | Não | `openai` | `openai` ou `google` |
| `LLM_MODEL` | Não | `gpt-4o-mini` | Modelo de geração |
| `EVAL_MODEL` | Não | `gpt-4o` | Modelo de avaliação (LLM-as-Judge) |
| `GOOGLE_API_KEY` | Sim (se google) | — | Chave Gemini |

---

## Ordem de execução (obrigatória)

```bash
source venv/bin/activate          # sempre deste projeto
python src/pull_prompts.py        # 1. pull v1 (opcional se v1.yml já existe)
pytest tests/test_prompts.py -v   # 2. validar estrutura do v2
python src/push_prompts.py        # 3. push v2 ao Hub
python src/evaluate.py            # 4. avaliar métricas
```

Scripts devem ser executados **a partir da raiz do projeto**.

---

## Métricas de aprovação

Todas devem ser ≥ 0.8 (não basta a média):

| Métrica | Cálculo |
|---------|---------|
| F1-Score | LLM-as-Judge: precision × recall dos fatos vs referência |
| Clarity | Média de organização, linguagem, ambiguidade, concisão |
| Precision | Ausência de alucinações, foco, correção factual |
| Helpfulness | `(Clarity + Precision) / 2` |
| Correctness | `(F1 + Precision) / 2` |

Última execução de referência (exemplo aprovado): Helpfulness 0.90, Correctness 0.86, F1 0.85, Clarity 0.93, Precision 0.87 — **com credenciais próprias**, não compartilhadas.

---

## Manutenção comum

| Tarefa | Ação |
|--------|------|
| Métrica abaixo de 0.8 | Editar `prompts/bug_to_user_story_v2.yml` → push → evaluate |
| Teste falhou | Verificar presença de `markdown`, `Product Manager`, `exemplo`/`entrada`/`saída`, 2+ técnicas no YAML |
| Push falhou (handle) | Criar handle em https://smith.langchain.com/prompts, atualizar `USERNAME_LANGSMITH_HUB` |
| pytest not found | Ativar venv deste projeto: `source venv/bin/activate` |
| ImportError hub | Mesma venv + `pip install -r requirements.txt` |
| Trocar provider | Alterar `LLM_PROVIDER`, `LLM_MODEL`, `EVAL_MODEL` no `.env` |

---

## Ciclo de iteração esperado

O desafio prevê **3-5 iterações**. Fluxo:

1. Rodar `evaluate.py` e anotar métricas por exemplo (F1 individual no terminal)
2. Identificar exemplos com F1 < 0.8 (geralmente persona, formato ou seções faltando)
3. Ajustar few-shots ou regras no v2.yml
4. `pytest` → `push_prompts.py` → `evaluate.py`
5. Repetir até todas ≥ 0.8

---

## Dependências entre arquivos

- `evaluate.py` → importa `metrics.py`, `utils.py`; puxa prompt do **Hub** (não do YAML local)
- `push_prompts.py` → lê YAML local e publica no Hub — **sempre push antes de evaluate**
- `pull_prompts.py` → independente; salva v1 localmente
- `tests/test_prompts.py` → valida apenas `prompts/bug_to_user_story_v2.yml`

---

## O que NÃO fazer

- Não commitar `.env` com chaves reais ou handle pessoal
- Não documentar credenciais, URLs ou handles de terceiros no README — use placeholders (`{seu_username}`, `{LANGSMITH_PROJECT}`)
- Não alterar `src/evaluate.py`, `src/metrics.py`, `src/utils.py` (fornecidos pelo desafio)
- Não alterar `datasets/bug_to_user_story.jsonl`
- Não usar venv de outro projeto (ex.: `langchain/.venv`)
- Não remover few-shot examples ou técnicas do YAML (testes falham)
- Não incluir substring `TODO` no `system_prompt`
- Não mover contexto de agente de volta para o README — manter neste arquivo

---

## Testes de validação

```bash
pytest tests/test_prompts.py -v
# Esperado: 7 passed

python src/evaluate.py
# Esperado: ✅ STATUS: APROVADO - Todas as métricas >= 0.8
```
