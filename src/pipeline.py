import torch
from src.config import *
from src.utils import *
from src.retriever import load_knowledge_graph, load_or_build_embeddings, load_reranker, retrieve_context, GATE_FAILURE_COUNTER
from src.llm_engine import load_model, unload_model, build_prompt, generate, clean_output

class POMPipeline:
    def __init__(self, model_id: str, label: str):
        self.model_id = model_id
        self.label = label
        self.is_rag = "RAG" in label
        
        # Load retriever components if needed
        self.G = None
        self.embed_model = None
        self.reranker = None
        self.triple_embeddings = None
        self.all_triples = None
        self.triple_texts = None
        
        if self.is_rag:
            log(f"Initializing RAG pipeline for {label}")
            self.G = load_knowledge_graph(KB_PATH, GRAPHML_PATH)
            
            from sentence_transformers import SentenceTransformer
            self.embed_model = SentenceTransformer(EMBED_MODEL)
            
            self.triple_embeddings, self.all_triples, self.triple_texts = load_or_build_embeddings(
                self.G, self.embed_model, TRIPLE_EMB_CACHE, KB_PATH
            )
            self.reranker = load_reranker()
            
        # Load the LLM
        log(f"Loading LLM {label}...")
        self.tokenizer, self.model = load_model(self.model_id, self.label)
        
    def __del__(self):
        if hasattr(self, 'model'):
            unload_model(self.model, self.label)
            
    def ask(self, question: str) -> tuple[str, bool, str]:
        context_text = ""
        gate_passed = False
        
        if self.is_rag:
            context_text, _, _, _, gate_scores = retrieve_context(
                question, self.embed_model, self.reranker, 
                self.triple_embeddings, self.all_triples, self.triple_texts,
                MMR_K_LARGE, G=self.G
            )
            score = gate_scores.get("confidence", 0.0)
            
            if score < GATE_CONFIDENCE_THRESHOLD or context_text == "":
                # Hard Fallback
                GATE_FAILURE_COUNTER[self.label] += 1
                context_text = ""
            else:
                gate_passed = True
                
        prompt = build_prompt(self.tokenizer, question, context_text)
        answer, _ = generate(self.tokenizer, self.model, prompt)
        
        return answer, gate_passed, context_text
