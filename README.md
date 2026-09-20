<div align="center">
  <h1>🧠 Agentic Knowledge Graph Pipeline</h1>
  <p><strong>A knowledge-graph assistant that retrieves locally, expands through a 120B backend when needed, and synthesizes answers with a local model.</strong></p>
</div>

<br>

This repository contains an **Agentic RAG (Retrieval-Augmented Generation) Pipeline**. It searches local knowledge first, calls the 120B backend only for missing facts, and optionally grounds a failed 120B lookup with web evidence before local answer synthesis.

## ✨ Core Architecture

*   **Knowledge Expansion (120B):** Generates missing triplets through `openai/gpt-oss-120b` only after local retrieval is insufficient.
*   **Local Quantized Model:** Uses a local HuggingFace model (`Qwen 3B`) with automatic Windows GPU 4-bit or CPU INT8 selection to synthesize the final answer.

## 🚀 Features

*   **Dynamic Knowledge Expansion:** The engine automatically extracts triplets `[Subject] (Relation) [Object]` from your prompts and injects them into a persistent `rag_knowledge.txt` database.
*   **Fact Provenance:** Facts generated from web research also create immutable records in `data/rag/fact_provenance.jsonl`, preserving the Tavily search query, source titles, URLs, excerpts, retrieval time, model, and verification status. The text knowledge base remains compatible with the existing retriever.
*   **Human Feedback Loop:** After each answer, mark it correct, incorrect, incomplete, or skip it. Feedback is retained in `data/rag/answer_feedback.jsonl`; incorrect and incomplete answers are also written to `data/rag/fact_review_queue.jsonl` for curator review with their implicated facts and source links.
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
3. Add your 120B backend key to `.env`:
   ```env
   GROQ_API_KEY="your-key"
   ```
4. *Note: You will need to download the local Qwen 3B model (or your preferred local synthesizer) into a `/local_qwen_3b` directory, which is excluded from source control.*

## 💻 Usage

Run the main agentic loop:
```bash
python -m src.rag_pipeline.agent
```

On Windows, the default `--runtime auto` always uses quantization: an NVIDIA CUDA GPU selects 4-bit NF4, while a CPU-only laptop selects PyTorch dynamic INT8. You can override the selection with `--runtime gpu-4bit` or `--runtime cpu-int8`.

Type your prompt and watch the dual-model architecture generate the knowledge graph, write the code into your vault, and stream the final answer back to you!
