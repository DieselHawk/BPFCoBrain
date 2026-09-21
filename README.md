# BPFCoBrain - Local AI Orchestration Layer

BPFCoBrain is a local-first AI orchestration system designed for high-reliability, offline-capable executive control. It leverages Ollama (Hermes 3) and a structured document lattice (Obsidian) to provide a unified brain for a fleet of specialized agents.

## 🚀 Quick Start

### 1. Prerequisites
- **Ollama**: Installed and running locally.
- **Model**: `hermes3:8b` pulled via `ollama pull hermes3:8b`.
- **Python 3.10+**: Installed with required dependencies from `requirements.txt`.

### 2. Execution
To launch the full system including the CEO Dashboard:
```bash
python launch_app.py
```
The Super Dashboard is available at: `http://127.0.0.1:5001`

## 🏗 Architecture

- **Core Brain**: `omniroute.py` handles intelligence routing.
- **Control Plane**: `ceo_dashboard.py` manages the Super Dashboard and agent status.
- **Interface**: `Dashboard/super_dashboard.html` provides the visual Command Center.
- **Agent Fleet**: Specialized agents (Bob, Cindy, Kai, Neo) operate via `agent_runtime.py`.
- **Knowledge**: Vault-indexed document lattice for RAG and context.

## 🛠 Key Features

- **Local-First**: Priority routing to Ollama.
- **Offline Mode**: Set `BPFCO_OFFLINE=1` to block all cloud API calls.
- **Human-in-the-Loop**: Approval gate for all external actions.
- **Super Dashboard**: Real-time agent state visualization and brain graph control.

## 📁 Project Structure

- `/Brain`: Executive state, logs, and security settings.
- `/Dashboard`: Server logic and frontend assets.
- `/Presence`: Avatar and voice integration layer.
- `ceo_dashboard.py`: The primary server for the command center.
- `omniroute.py`: The AI routing logic.

## 🛡 Security & Governance
- All external actions are routed through `approval_gate.py`.
- State is persisted in `Brain/Executive/state.json`.
