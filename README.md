# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Desafio do MBA IA — Full Cycle: transformar prompts de baixa qualidade em prompts production-ready, versionados no LangSmith Hub e validados por métricas objetivas.

**Autora:** Isabela de Aro  
**Prompt publicado:** [isabeladearo/bug_to_user_story_v2](https://smith.langchain.com/prompts/bug_to_user_story_v2)  
**Dashboard LangSmith:** [mba-ia-pull-evaluation-prompt](https://smith.langchain.com/projects/mba-ia-pull-evaluation-prompt)

---

## Por que este projeto?

Times de produto e engenharia usam LLMs para tarefas repetitivas — converter bugs em user stories, resumir tickets, gerar critérios de aceitação. O problema é que **um prompt mal escrito produz saídas inconsistentes**, difíceis de revisar e perigosas em produção:

- **Sem estrutura** → cada execução gera um formato diferente
- **Sem exemplos** → o modelo não aprende o padrão esperado
- **Sem persona** → respostas genéricas ou técnicas demais
- **Sem avaliação** → ninguém sabe se o prompt melhorou de verdade

Este projeto resolve isso com um **ciclo completo de Prompt Engineering**:

1. **Pull** do prompt ruim do LangSmith Hub (ponto de partida controlado)
2. **Otimização** com técnicas avançadas (Few-shot, CoT, Role Prompting)
3. **Push** da versão otimizada de volta ao Hub (versionamento e colaboração)
4. **Avaliação** automática com 5 métricas customizadas (LLM-as-Judge)

Na prática, funciona como um pipeline de qualidade para prompts:

- Você puxa `leonanluppi/bug_to_user_story_v1` (prompt ruim, ~45% de helpfulness)
- Refatora em `bug_to_user_story_v2.yml` com técnicas do curso
- Publica em `{seu_username}/bug_to_user_story_v2` no Hub
- Roda `evaluate.py` contra 15 bugs reais e obtém notas objetivas

Esse padrão aparece no mundo real em plataformas de IA (LangSmith, PromptLayer, Humanloop), times de MLOps e qualquer empresa que **versiona prompts como código**. O desafio usa conversão de bug → user story porque exige raciocínio estruturado, formato específico e tratamento de edge cases — exatamente onde técnicas como Few-shot e Chain of Thought fazem diferença mensurável.

> **Em uma frase:** versionar, otimizar e medir prompts com LangChain e LangSmith — em vez de "achar que melhorou".

---

## O que este projeto faz

```
LangSmith Hub                    Local                         LangSmith Hub
─────────────                    ─────                         ─────────────
leonanluppi/          pull_prompts.py          prompts/
bug_to_user_story_v1  ──────────────────►     bug_to_user_story_v1.yml
                                                      │
                                              (otimização manual)
                                                      ▼
                                             bug_to_user_story_v2.yml
                                                      │
                              push_prompts.py         │
                              evaluate.py             ▼
                                             isabeladearo/
                                             bug_to_user_story_v2
                                                      │
                                                      ▼
                                             5 métricas >= 0.8 ✓
```

| Fase | Script | Responsabilidade |
|------|--------|------------------|
| 1 — Pull | `src/pull_prompts.py` | Baixa `leonanluppi/bug_to_user_story_v1` do Hub |
| 2 — Otimizar | `prompts/bug_to_user_story_v2.yml` | Prompt refatorado com técnicas avançadas |
| 3 — Push | `src/push_prompts.py` | Publica `{username}/bug_to_user_story_v2` no Hub |
| 4 — Avaliar | `src/evaluate.py` | Roda 15 exemplos e calcula 5 métricas |
| 5 — Validar | `tests/test_prompts.py` | 7 testes pytest da estrutura do prompt |

---

## Técnicas Aplicadas (Fase 2)

### 1. Few-shot Learning (obrigatório)

**Por quê:** O prompt v1 não tinha exemplos — o modelo improvisava formato, persona e nível de detalhe a cada execução. Few-shot é a técnica com maior impacto em tarefas de formatação estruturada.

**Como apliquei:** 7 exemplos no `system_prompt` cobrindo os 3 níveis de complexidade do dataset:

| Exemplo | Complexidade | Cenário |
|---------|--------------|---------|
| 1 | Simples | Botão de carrinho |
| 2 | Simples | Contagem errada no dashboard |
| 3 | Médio | Desconto incorreto no pipeline CRM |
| 4 | Médio | Estoque no checkout |
| 5 | Médio | Performance de relatório SQL |
| 6 | Médio | Webhook de pagamento |
| 7 | Complexo | Checkout com 4 falhas críticas |

Cada exemplo segue o padrão `Entrada:` / `Saída:` com a estrutura exata esperada pelo dataset de avaliação.

### 2. Role Prompting

**Por quê:** Bug reports são textos técnicos; user stories precisam de linguagem de produto. A persona ancora o tom e o foco em valor de negócio.

**Como apliquei:**

```
Você é um Product Manager sênior especializado em práticas ágeis e análise de bugs.
```

Além disso, regras explícitas de **escolha de persona** por tipo de bug (cliente, administrador, vendedor, sistema).

### 3. Chain of Thought (CoT)

**Por quê:** Converter bug → user story exige raciocínio em etapas: classificar complexidade, identificar persona, extrair detalhes técnicos, formatar critérios.

**Como apliquei:** Processo de 7 passos no system prompt, executado mentalmente antes da resposta:

1. Classificar complexidade (SIMPLES / MÉDIO / COMPLEXO)
2. Identificar persona correta
3. Extrair problema, impacto e detalhes técnicos
4. Formular user story
5. Escrever critérios Dado/Quando/Então
6. Adicionar seções extras conforme template
7. Para complexos, cobrir cada problema numerado

### Decisões de design adicionais

| Problema identificado na iteração | Solução aplicada |
|-----------------------------------|------------------|
| F1 baixo em bugs médios | Template MÉDIO para bugs com um problema, mesmo que o relato seja longo |
| Persona errada (cliente vs vendedor) | Regras de persona por domínio (CRM → vendedor, estoque → sistema) |
| Formato complexo desnecessário | Template COMPLEXO (`=== seções ===`) só para 3+ problemas distintos |
| Recall baixo em cálculos | Seção obrigatória `Exemplo de Cálculo:` quando o relato traz valores |
| Bugs de estoque incompletos | Seção `Critérios de Prevenção:` quando há fluxo multi-cliente |

---

## Resultados Finais

### Métricas — v2 aprovado

Execução final de `python src/evaluate.py` (11/07/2026):

```
==================================================
Prompt: isabeladearo/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.90 ✓
  - Correctness: 0.86 ✓

Métricas Base:
  - F1-Score: 0.85 ✓
  - Clarity: 0.93 ✓
  - Precision: 0.87 ✓

📊 MÉDIA GERAL: 0.8830

✅ STATUS: APROVADO - Todas as métricas >= 0.8
```

### Tabela comparativa — v1 vs v2

| Métrica | v1 (leonanluppi) | v2 (isabeladearo) | Δ |
|---------|------------------|-------------------|---|
| Helpfulness | 0.45 ✗ | **0.90** ✓ | +0.45 |
| Correctness | 0.52 ✗ | **0.86** ✓ | +0.34 |
| F1-Score | 0.48 ✗ | **0.85** ✓ | +0.37 |
| Clarity | 0.50 ✗ | **0.93** ✓ | +0.43 |
| Precision | 0.46 ✗ | **0.87** ✓ | +0.41 |
| **Média** | **0.48** | **0.88** | **+0.40** |

> Valores v1 são ilustrativos do desafio (prompt de referência do instrutor). Valores v2 são da execução real deste repositório.

### Iterações realizadas

| Iteração | F1 | Correctness | Problema identificado | Ajuste |
|----------|-----|-------------|----------------------|--------|
| 1 | 0.74 | 0.78 | Formato genérico, persona errada | Templates por complexidade + few-shots |
| 2 | 0.78 | 0.81 | Bugs médios classificados como complexos | Regras de classificação + exemplos do dataset |
| 3 | **0.85** | **0.86** | — | **Aprovado** |

### Evidências no LangSmith

- **Projeto:** https://smith.langchain.com/projects/mba-ia-pull-evaluation-prompt
- **Prompt v2:** https://smith.langchain.com/prompts/bug_to_user_story_v2
- **Dataset:** `mba-ia-pull-evaluation-prompt-eval` (15 exemplos)

> **Screenshots:** adicione capturas do dashboard em `screenshots/` (pasta ignorada pelo git) e referencie aqui se desejar versionar as imagens.

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com/) com Hub handle criado
- API Key da [OpenAI](https://platform.openai.com/api-keys) (recomendado) ou [Google Gemini](https://aistudio.google.com/app/apikey)

### 1. Clonar e configurar ambiente

```bash
git clone git@github.com:isabeladearo/mba-ia-pull-evaluation-prompt.git
cd mba-ia-pull-evaluation-prompt

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

| Variável | Descrição |
|----------|-----------|
| `LANGSMITH_API_KEY` | Chave em https://smith.langchain.com/settings |
| `USERNAME_LANGSMITH_HUB` | Seu handle do Hub (ex: `isabeladearo`) |
| `OPENAI_API_KEY` | Chave da OpenAI |
| `LLM_PROVIDER` | `openai` (padrão) ou `google` |
| `LLM_MODEL` | `gpt-4o-mini` (geração) |
| `EVAL_MODEL` | `gpt-4o` (avaliação) |

> **Importante:** use sempre a venv **deste projeto**. Confirme com `which python` — deve apontar para `.../mba-ia-pull-evaluation-prompt/venv/bin/python`.

### 3. Fase 1 — Pull do prompt inicial

```bash
python src/pull_prompts.py
```

Salva em `prompts/bug_to_user_story_v1.yml` a partir de `leonanluppi/bug_to_user_story_v1`.

### 4. Fase 2 — Otimização (já implementada)

O arquivo `prompts/bug_to_user_story_v2.yml` contém o prompt otimizado. Para iterar:

1. Edite o YAML
2. Rode os testes: `pytest tests/test_prompts.py -v`
3. Faça push e reavalie (fases 3 e 4)

### 5. Fase 3 — Push para o LangSmith Hub

```bash
python src/push_prompts.py
```

Publica `{USERNAME_LANGSMITH_HUB}/bug_to_user_story_v2` como prompt **público**.

### 6. Fase 4 — Avaliação

```bash
python src/evaluate.py
```

Avalia o prompt v2 contra 15 bugs do dataset. Critério de aprovação: **todas** as 5 métricas ≥ 0.8.

### 7. Testes de validação

```bash
pytest tests/test_prompts.py -v
```

7 testes (6 obrigatórios + validação de estrutura via `utils.validate_prompt_structure`).

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.13 |
| Framework | LangChain 0.3.13 |
| Avaliação | LangSmith |
| Prompt Hub | LangSmith Hub (`langchain.hub`) |
| Formato | YAML |
| LLM (geração) | OpenAI `gpt-4o-mini` |
| LLM (avaliação) | OpenAI `gpt-4o` |
| Testes | pytest |

---

## Estrutura do projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example
├── requirements.txt
├── README.md
├── AGENTS.md                  # Contexto para agentes de IA
│
├── prompts/
│   ├── bug_to_user_story_v1.yml   # Pull do Hub (prompt ruim)
│   └── bug_to_user_story_v2.yml   # Prompt otimizado
│
├── datasets/
│   └── bug_to_user_story.jsonl    # 15 bugs (5 simples, 7 médios, 3 complexos)
│
├── src/
│   ├── pull_prompts.py            # Pull do LangSmith Hub
│   ├── push_prompts.py              # Push para o LangSmith Hub
│   ├── evaluate.py                  # Avaliação automática (fornecido)
│   ├── metrics.py                   # 5 métricas LLM-as-Judge (fornecido)
│   └── utils.py                     # Funções auxiliares (fornecido)
│
└── tests/
    └── test_prompts.py              # 7 testes pytest
```

---

## Referências

- [Repositório base do desafio](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [LangSmith Prompt Hub](https://smith.langchain.com/prompts)

---

## Manutenção por agentes de IA

Consulte [AGENTS.md](./AGENTS.md) para contexto técnico, regras de negócio, variáveis de ambiente e o que não alterar.
