import time

# Colors for terminal styling
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

# =====================================================================
#             PARADIGM 1: LANGCHAIN (Chain & Agent Paradigm)
# =====================================================================
class LangChainMock:
    """
    Simulates LangChain Expression Language (LCEL) and Chain execution.
    LangChain focuses on chaining components: PromptTemplate -> LLM -> OutputParser.
    """
    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template
        
    def invoke(self, inputs: dict) -> str:
        # Construct prompt
        prompt = self.prompt_template.format(**inputs)
        print(f"  {Color.CYAN}[LangChain LCEL] Formulated Prompt:{Color.END}\n  \"\"\"{prompt}\"\"\"")
        time.sleep(0.5)
        # Simulate LLM reasoning and output
        return f"Hello {inputs['user_name']}, I processed your request using LangChain."

# =====================================================================
#             PARADIGM 2: LLAMAINDEX (Data Indexing Paradigm)
# =====================================================================
class LlamaIndexMock:
    """
    Simulates LlamaIndex document indexing and semantic retrieval.
    LlamaIndex focuses on connecting data sources (Documents -> Nodes -> Index -> Query Engine).
    """
    def __init__(self, documents: list[str]):
        self.documents = documents
        
    def query(self, query_str: str) -> str:
        print(f"  {Color.YELLOW}[LlamaIndex Index] Running Semantic Retrieval for Query: '{query_str}'{Color.END}")
        time.sleep(0.5)
        # Simulate index search and node matching
        matching_nodes = [doc for doc in self.documents if any(word in doc.lower() for word in query_str.lower().split())]
        
        if matching_nodes:
            context = " ".join(matching_nodes)
            return f"Context retrieved: \"{context}\"\nSynthesis Answer: The facts state that {context}"
        return "No relevant facts found in vector index."

# =====================================================================
#                         LAB SESSION EXECUTION
# =====================================================================
def run_lab_sessions_comparison():
    print(f"{Color.BOLD}====================================================================={Color.END}")
    print(f"{Color.BOLD}   LAB SESSION L1.2: LANGCHAIN VS LLAMAINDEX COMPILATION & STUDY     {Color.END}")
    print(f"{Color.BOLD}====================================================================={Color.END}\n")

    # 1. Demonstrate LangChain (Chain / Pipeline construction)
    print(f"{Color.BOLD}1. Executing LangChain Pipeline...{Color.END}")
    prompt_template = "System: You are a helpful assistant.\nUser: Hello, my name is {user_name}. Help me with: {task}\nAssistant:"
    chain = LangChainMock(prompt_template)
    
    result = chain.invoke({"user_name": "Ada Lovelace", "task": "Learn agent systems"})
    print(f"  {Color.GREEN}[LangChain Response]{Color.END} {result}\n")

    time.sleep(1.0)

    # 2. Demonstrate LlamaIndex (Data ingestion & Index querying)
    print(f"{Color.BOLD}2. Executing LlamaIndex Search Index...{Color.END}")
    documents = [
        "Devin is an autonomous software engineering task solver.",
        "Perplexity is a real-time web-scale search synthesizer."
    ]
    # Ingest documents and create vector index
    index = LlamaIndexMock(documents)
    # Query index
    response = index.query("Explain Devin functionality")
    print(f"  {Color.GREEN}[LlamaIndex Response]{Color.END}\n  {response}\n")

    # 3. Key Theoretical Study Differences
    print(f"{Color.BOLD}====================================================================={Color.END}")
    print(f"{Color.BOLD}                 KEY COMPARATIVE PARADIGM STUDY                      {Color.END}")
    print(f"{Color.BOLD}====================================================================={Color.END}")
    print("""
| Feature | LangChain Paradigm | LlamaIndex Paradigm |
| :--- | :--- | :--- |
| **Core Abstraction** | Chaining LLM calls (LCEL, chains, prompt templates). | Retrieving and indexing external data sources (Indexes, Documents, Nodes). |
| **Primary Use Case** | Building interactive conversational agents, tools networks, and task executors. | Search-augmenting LLMs (RAG - Retrieval Augmented Generation) on private/custom files. |
| **Agent Paradigm** | Highly customizable agent loop using LangGraph and tools binders. | Simple Query Engines and Data Agents optimized for context retrieval. |
| **Data Ingestion** | Secondary focus (handled via simple loaders and document helpers). | Core focus (advanced vector indexes, sentence window retrievers, metadata extraction). |
    """)
    print(f"{Color.BOLD}====================================================================={Color.END}")

if __name__ == "__main__":
    run_lab_sessions_comparison()
