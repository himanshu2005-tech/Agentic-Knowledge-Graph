import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GEMMA_PATH       = os.path.join(BASE_DIR, "local_gemma_2_2b_it")
QWEN_PATH        = os.path.join(BASE_DIR, "local_qwen_3b")
LLAMA_PATH       = os.path.join(BASE_DIR, "local_llama_3b")

KB_PATH          = os.path.join(BASE_DIR, "data", "kg", "knowledge_base.txt")
GRAPHML_PATH     = os.path.join(BASE_DIR, "data", "knowledge_graph.graphml")
QUESTIONS_PATH   = os.path.join(BASE_DIR, "data", "questions.json")
RESULTS_PATH     = os.path.join(BASE_DIR, "data", "eval_results_v7.json")
TRIPLE_EMB_CACHE = os.path.join(BASE_DIR, "data", "triple_embeddings.pkl")

EMBED_MODEL      = "BAAI/bge-large-en-v1.5"

# Round-Robin Domain Scheduler
BEAM_EMBED_MODEL = "all-MiniLM-L6-v2"

DOMAIN_CATEGORIES = {
    "ComputerScience": "Computer Science, Programming, Software Engineering, Algorithms, Data Structures, Operating Systems",
    "Mathematics": "Mathematics, Algebra, Calculus, Geometry, Statistics, Number Theory, Topology",
    "Physics": "Physics, Mechanics, Thermodynamics, Quantum Mechanics, Electromagnetism, Optics, Relativity",
    "Chemistry": "Chemistry, Organic Chemistry, Inorganic Chemistry, Biochemistry, Chemical Reactions, Elements",
    "Biology": "Biology, Genetics, Evolution, Ecology, Microbiology, Anatomy, Cell Biology, Physiology",
    "Medicine": "Medicine, Surgery, Pharmacology, Pathology, Immunology, Cardiology, Oncology, Diagnosis",
    "History": "History, Ancient Civilizations, Wars, Revolutions, Historical Figures, Empires, Colonies",
    "Philosophy": "Philosophy, Ethics, Logic, Metaphysics, Epistemology, Existentialism, Stoicism",
    "Economics": "Economics, Microeconomics, Macroeconomics, Finance, Markets, Trade, Banking, GDP",
    "PoliticalScience": "Political Science, Government, Democracy, Law, International Relations, Constitution",
    "Psychology": "Psychology, Cognitive Science, Behavioral Science, Neuroscience, Mental Health, Therapy",
    "Linguistics": "Linguistics, Language, Grammar, Phonology, Semantics, Syntax, Translation",
    "Arts": "Art, Music, Literature, Cinema, Theater, Painting, Sculpture, Poetry, Architecture",
    "Geography": "Geography, Geology, Oceanography, Meteorology, Climate, Continents, Rivers, Mountains",
    "Engineering": "Engineering, Civil Engineering, Mechanical Engineering, Electrical Engineering, Aerospace",
    "Sociology": "Sociology, Culture, Society, Anthropology, Demographics, Social Movements, Religion",
    "Astronomy": "Astronomy, Cosmology, Astrophysics, Solar System, Stars, Galaxies, Black Holes, Nebula",
    "Sports": "Sports, Athletics, Olympics, Football, Basketball, Tennis, Cricket, Swimming, Chess",
    "Business": "Business, Management, Marketing, Entrepreneurship, Accounting, Leadership, Strategy",
    "EnvironmentalScience": "Environmental Science, Climate Change, Ecology, Conservation, Renewable Energy, Pollution",
}
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MAX_NEW_TOKENS   = 350

TOP_K               = 30
MMR_K_SMALL         = 4
MMR_K_LARGE         = 8
MMR_LAMBDA          = 0.8
GENERIC_PENALTY     = 0.30
MIN_WORDS_PER_LINE  = 3

GATE_WEIGHTS = {"semantic": 0.30, "rerank": 0.35, "lexical": 0.20, "structure": 0.15}
GATE_CONFIDENCE_THRESHOLD = 0.40

SYSTEM_INSTRUCTION = (
    "You are a strictly factual assistant. Answer questions accurately and concisely "
    "in 2-3 sentences. Do not use markdown, bullet points, or numbered lists. "
    "Do not repeat yourself. If you are unsure, say 'I do not know.'"
)

RAG_INSTRUCTION_SUFFIX = (
    " You are also given background facts below. These facts are the absolute truth. "
    "You must prioritize these facts over your own prior knowledge, even if they contradict what you know."
)

SYSTEMS = {
    "qwen_raw": "Qwen 3B (Raw)",
    "gemma_raw": "Gemma 2B (Raw)",
    "gemma_rag": "Gemma 2B + KG-RAG",
    "llama_raw": "Llama 3B (Raw)",
    "llama_rag": "Llama 3B + KG-RAG",
}

RAG_TO_RAW = {"gemma_rag": "gemma_raw", "llama_rag": "llama_raw"}
