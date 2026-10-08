import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Config(BaseSettings):
    """Configuration for Knowledge Graph Generation."""
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    base_dir: str = Field(default=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # Model Config
    model_id: str = Field(default="local_qwen_3b", description="Model folder name or HF repo id")
    temperature: float = Field(default=0.05)
    max_new_tokens: int = Field(default=350)
    top_k: int = Field(default=30)
    
    
    # File Paths (relative to base_dir/data unless absolute)
    data_dir: str = Field(default="data/kg")
    
    @property
    def data_path(self) -> str:
        if os.path.isabs(self.data_dir):
            return self.data_dir
        return os.path.join(self.base_dir, self.data_dir)

    @property
    def model_path(self) -> str:
        if os.path.isabs(self.model_id):
            return self.model_id
        return os.path.join(self.base_dir, self.model_id)

    @property
    def output_file(self) -> str: return os.path.join(self.data_path, "knowledge_base.txt")
    @property
    def visited_file(self) -> str: return os.path.join(self.data_path, "visited_nodes.txt")
    @property
    def queue_file(self) -> str: return os.path.join(self.data_path, "queue_checkpoint.txt")
    @property
    def blacklist_file(self) -> str: return os.path.join(self.data_path, "blacklisted_nodes.txt")
    @property
    def triplet_set_file(self) -> str: return os.path.join(self.data_path, "triplet_set.json")
    @property
    def stats_log_file(self) -> str: return os.path.join(self.data_path, "bfs_stats.log")
    @property
    def quarantine_file(self) -> str: return os.path.join(self.data_path, "conflicting_triples.txt")
    @property
    def filtered_file(self) -> str: return os.path.join(self.data_path, "filtered_placeholders.txt")
    @property
    def corroboration_file(self) -> str: return os.path.join(self.data_path, "corroboration_counts.json")
    @property
    def wikidata_cache_file(self) -> str: return os.path.join(self.data_path, "wikidata_cache.json")
    @property
    def polysemy_log_file(self) -> str: return os.path.join(self.base_dir, "data", "polysemy_flagged.txt")

    # Features
    enable_wikidata_verification: bool = Field(default=False)
    
    def setup_dirs(self):
        """Ensure necessary directories exist."""
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "data"), exist_ok=True)

settings = Config()
