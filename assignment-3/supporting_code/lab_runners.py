import os
import time
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# --- L3.1 Context Window Summarization ---
class ContextManager:
    """
    Simulates context window management: monitors token counts, slides the window,
    and compresses/summarizes older logs when thresholds are exceeded.
    """
    def __init__(self, max_tokens: int = 400):
        self.max_tokens = max_tokens
        self.history: List[Dict[str, str]] = []
        
    def estimate_tokens(self, text: str) -> int:
        # Simple token estimation: ~1.3 tokens per word
        return int(len(text.split()) * 1.3)
        
    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        
    def get_total_tokens(self) -> int:
        return sum(self.estimate_tokens(msg["content"]) for msg in self.history)
        
    def compress_context(self, api_client=None) -> Tuple[str, int, int]:
        """
        Compresses history: summarizes turns 1 to N-2, while keeping the last 2 turns intact.
        """
        before_tokens = self.get_total_tokens()
        if before_tokens <= self.max_tokens or len(self.history) <= 3:
            return "No compression needed.", before_tokens, before_tokens
            
        # Separate old messages to summarize and recent messages to keep
        to_summarize = self.history[:-2]
        to_keep = self.history[-2:]
        
        # Prepare text for summarization
        text_to_summarize = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in to_summarize])
        
        summary = ""
        
        # Call Gemini if API client is available
        if api_client:
            try:
                prompt = (
                    "Summarize the following conversation history into a concise paragraph "
                    "capturing all key factual information, names, preferences, and progress. "
                    "This summary will serve as the compressed long-term context buffer for an agent:\n\n"
                    + text_to_summarize
                )
                response = api_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                summary = response.text.strip()
            except Exception as e:
                print(f"[L3.1] API summarization failed: {e}. Using simulated summary.")
                summary = ""
                
        if not summary:
            # Fallback local simulation of summary
            summary = (
                "The conversation started with Armaan (Research Intern) introducing himself "
                "and his work on the Ada Lovelace agent project. He specified that he prefers Streamlit for UI prototyping "
                "and corrected his database choice from ChromaDB to a NumPy-based vector store to avoid C++ build issues."
            )
            
        # Reconstruct history
        self.history = [
            {"role": "system", "content": f"System Summary of past conversation: {summary}"}
        ] + to_keep
        
        after_tokens = self.get_total_tokens()
        return summary, before_tokens, after_tokens


# --- L3.2 Long-Term Vector Memory Operations ---
class VectorMemoryShowcase:
    """Shows how text is embedded, stored, and retrieved using vector dot products."""
    def __init__(self, embedding_function):
        self.embedding_function = embedding_function
        self.store: List[Dict[str, Any]] = []
        
    def add_chunk(self, doc_id: str, text: str):
        vector = self.embedding_function(text)
        self.store.append({
            "id": doc_id,
            "text": text,
            "vector": np.array(vector)
        })
        
    def search(self, query_text: str, k: int = 1) -> List[Tuple[str, float]]:
        if not self.store:
            return []
        query_vector = np.array(self.embedding_function(query_text))
        results = []
        for item in self.store:
            # Compute cosine similarity
            v = item["vector"]
            similarity = np.dot(query_vector, v) / (np.linalg.norm(query_vector) * np.linalg.norm(v))
            results.append((item["text"], float(similarity)))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]


# --- L3.3 Knowledge Graph with NetworkX ---
class ConceptKnowledgeGraph:
    """Constructs and renders a concept relationship graph for the personal assistant."""
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_default_graph()
        
    def _build_default_graph(self):
        # Nodes
        self.graph.add_node("Armaan", type="User", desc="Research Intern")
        self.graph.add_node("Ada Lovelace", type="Project", desc="Agentic AI Internship Project")
        self.graph.add_node("Streamlit", type="Framework", desc="UI Prototyping framework")
        self.graph.add_node("NumPy Store", type="Database", desc="Lightweight Vector Store")
        
        # Edges
        self.graph.add_edge("Armaan", "Ada Lovelace", relation="WORK_ON")
        self.graph.add_edge("Armaan", "Streamlit", relation="PREFER_UI")
        self.graph.add_edge("Armaan", "NumPy Store", relation="PREFER_DB")
        self.graph.add_edge("Ada Lovelace", "Streamlit", relation="FRONTEND")
        self.graph.add_edge("Ada Lovelace", "NumPy Store", relation="MEMORY_BACKEND")
        
    def add_concept(self, source: str, target: str, relation: str):
        self.graph.add_edge(source, target, relation=relation)
        
    def render_graph(self, save_path: str = "knowledge_graph.png"):
        plt.figure(figsize=(8, 6), facecolor="#0e1117")
        ax = plt.gca()
        ax.set_facecolor("#0e1117")
        
        # Define layout
        pos = nx.spring_layout(self.graph, seed=42)
        
        # Custom coloring based on Node types
        node_colors = []
        for node, attrs in self.graph.nodes(data=True):
            node_type = attrs.get("type", "General")
            if node_type == "User":
                node_colors.append("#ff4b4b") # stream lit red
            elif node_type == "Project":
                node_colors.append("#00f0ff") # cyan
            elif node_type == "Framework":
                node_colors.append("#ffd700") # gold
            elif node_type == "Database":
                node_colors.append("#00ff66") # emerald green
            else:
                node_colors.append("#a0a0a0") # grey
                
        # Draw Nodes
        nx.draw_networkx_nodes(
            self.graph, pos, 
            node_color=node_colors, 
            node_size=2000, 
            alpha=0.9,
            edgecolors="#ffffff",
            linewidths=1.5
        )
        
        # Draw Edges
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color="#888888",
            width=2,
            arrowsize=20,
            arrowstyle="-|>"
        )
        
        # Labels
        nx.draw_networkx_labels(
            self.graph, pos,
            font_size=10,
            font_color="#ffffff",
            font_weight="bold"
        )
        
        # Edge Labels
        edge_labels = nx.get_edge_attributes(self.graph, "relation")
        nx.draw_networkx_edge_labels(
            self.graph, pos,
            edge_labels=edge_labels,
            font_color="#cccccc",
            font_size=8,
            bbox=dict(facecolor="#1a1c24", edgecolor="none", boxstyle="round,pad=0.2")
        )
        
        plt.title("User Profile & Context Knowledge Graph (L3.3)", color="#ffffff", fontsize=12, fontweight="bold", pad=15)
        plt.axis("off")
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, format="png", dpi=150, facecolor="#0e1117")
        plt.close()
        print(f"[GRAPH] Knowledge Graph rendered and saved to: {save_path}")


if __name__ == "__main__":
    # Test L3.3 rendering
    graph = ConceptKnowledgeGraph()
    graph.render_graph("test_graph.png")
    if os.path.exists("test_graph.png"):
        os.remove("test_graph.png")
