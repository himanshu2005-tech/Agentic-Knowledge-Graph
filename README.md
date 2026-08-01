<div align="center">
  <h1>🧠 Agentic Knowledge Graph Pipeline</h1>
  <p><strong>A Dual-Model AI Engine that dynamically expands its knowledge base and autonomously writes multi-domain code into a local vault.</strong></p>
</div>

<br>

This repository contains a cutting-edge **Agentic RAG (Retrieval-Augmented Generation) Pipeline**. It uses a dual-model architecture to achieve lightning-fast response times and unparalleled generation quality.

## ✨ Core Architecture

*   **The Brain (Groq 70B API):** Handles heavy knowledge extraction, context evaluation, and writes raw code for simulations, games, and web apps.
*   **The Synthesizer (Local 3B GPU):** Uses a local HuggingFace model (`Qwen 3B`) to rapidly synthesize factual responses and stream them directly to the terminal, avoiding heavy API limits for conversational text.

## 🚀 Features

*   **Dynamic Knowledge Expansion:** The engine automatically extracts triplets `[Subject] (Relation) [Object]` from your prompts and injects them into a persistent `rag_knowledge.txt` database.
*   **Autonomous Code Vault:** If the LLM determines you need a simulation or UI, it generates the raw code (Python, HTML5, GLSL, OpenSCAD, etc.) and seamlessly saves it to a local `/codevault` directory.
*   **Auto-Versioning:** Never lose your work. The pipeline automatically versions generated files (`_v2`, `_v3`) or prompts you for overwrites.
*   **Real-time Streaming:** Uses HuggingFace `TextIteratorStreamer` to deliver instantaneous, typewriter-style responses.

## 🛠️ Installation & Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/himanshu2005-tech/Agentic-Knowledge-Graph.git
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY="your-api-key-here"
   ```
4. *Note: You will need to download the local Qwen 3B model (or your preferred local synthesizer) into a `/local_qwen_3b` directory, which is excluded from source control.*

## 💻 Usage

Run the main agentic loop:
```bash
python -m src.rag_pipeline.agent
```

Type your prompt and watch the dual-model architecture generate the knowledge graph, write the code into your vault, and stream the final answer back to you!
