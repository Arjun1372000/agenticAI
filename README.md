# Deterministic MCP-Driven AI Agents for Ball Bearing Vibration Diagnostics

**Python Version:** `3.12.10`

**Dataset:** [NASA Bearing Dataset](https://www.kaggle.com/datasets/vinayak123tyagi/bearing-dataset)

## Setup

Create and activate the virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install the project dependencies:

```powershell
python -m pip install -e .
```

Make sure the NASA Bearing Dataset is placed inside:

```text
bearing-dataset/
```

Generate the processed feature dataset:

```powershell
python scripts/build_test2_features.py
```

Make sure Ollama is installed and `llama3.2` is available:

```powershell
ollama list
```

If required:

```powershell
ollama pull llama3.2
```

## Run the Project

Open **3 terminals** in the project root.

### Terminal 1 — FastAPI Backend

```powershell
uvicorn predictive_maintenance.api:app --reload
```

### Terminal 2 — MCP Server

```powershell
python -m predictive_maintenance.mcp_server
```

### Terminal 3 — AI Agent

```powershell
python scripts/run_agent.py
```

The monitoring dashboard is located at:

```text
frontend/index.html
```

## Run on Another Device

Install:

- Python `3.12.10`
- Ollama

Then:

1. Create and activate the virtual environment.
2. Run `python -m pip install -e .`
3. Install the Ollama model with `ollama pull llama3.2`.
4. Place the NASA Bearing Dataset in `bearing-dataset/`.
5. Run `python scripts/build_test2_features.py`.
6. Start the FastAPI backend, MCP server, and AI agent using the commands above.

> The raw dataset and generated processed/model artifacts are excluded from Git and must be generated locally.
