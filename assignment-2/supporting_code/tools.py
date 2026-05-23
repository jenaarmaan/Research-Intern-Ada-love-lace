import sys
import io
import traceback
import urllib.parse

class SearchTool:
    """
    Queries a local robust mock web index containing comprehensive real-world-style facts.
    Includes built-in failures for query testing and validation of agent re-planning.
    """
    def __init__(self):
        # A rich mock search database covering finance, statistics, geography, history, and science
        self.database = {
            "apple revenue 2024": "Apple Inc. (AAPL) reported an annual revenue of $391.0 billion for the fiscal year 2024, showing steady growth in services.",
            "microsoft revenue 2024": "Microsoft Corp. (MSFT) announced a fiscal year 2024 revenue of $245.1 billion, driven by robust cloud and AI expansions.",
            "google revenue 2024": "Alphabet Inc. (Google) reported total revenue of $307.4 billion for the year 2024, led by advertising and Google Cloud operations.",
            
            "apple assets 2024": "Apple Inc. (AAPL) balance sheet for fiscal year 2024 reports Total Assets of $321.8 billion.",
            "apple liabilities 2024": "Apple Inc. (AAPL) balance sheet for fiscal year 2024 reports Total Liabilities of $250.2 billion.",
            "apple equity 2024": "Apple Inc. (AAPL) reported Total Shareholder Equity of $71.6 billion for the fiscal year 2024.",
            
            "paris population": "Paris, the historic capital of France, has a city center population of approximately 2.1 million, with an urban area population exceeding 11 million.",
            "tokyo population": "Tokyo is the world's most populous metropolitan area, with a population estimated at approximately 37.4 million residents in 2024.",
            "new york population": "New York City, USA, has a population of approximately 8.3 million inside its five boroughs.",
            
            "alan turing birth year": "Alan Turing, the visionary mathematician and computer science pioneer, was born in London, United Kingdom, on June 23, 1912.",
            "london country": "London is the capital of England and the United Kingdom, positioned on the River Thames.",
            "united kingdom capital": "London is the capital and largest metropolitan city of England and the United Kingdom.",
            "england capital": "London is the capital city of England.",
            
            "flaky database url": "The central economics repository is hosted at 'https://flaky-database.api/data'. If it experiences network load issues, a secondary mirror is available at 'https://backup-database.api/data'.",
            "central economics repository": "The central economics repository is hosted at 'https://flaky-database.api/data' with mirror at 'https://backup-database.api/data'."
        }
        self.query_count = 0

    def run(self, query: str) -> str:
        self.query_count += 1
        query_clean = query.strip().lower()
        
        # Validation checks to trigger agent re-planning
        if not query_clean:
            return "Error: Search query cannot be empty."
        
        if len(query_clean) < 3:
            return "Error: Search query must be at least 3 characters long."
            
        # Simulating search index failures or warnings for specific queries
        if "empty query" in query_clean:
            return "Error: Invalid request parameters."
        
        if "flaky search" in query_clean:
            return "Error: Search service timeout. (HTTP 504 Gateway Timeout)"

        # Search matching: check for exact or substring matches in database
        matches = []
        for key, value in self.database.items():
            if key in query_clean or query_clean in key:
                matches.append(value)
                
        if matches:
            return " | ".join(matches)
        
        # Fallback to smart parsing for keywords
        keywords = query_clean.split()
        keyword_matches = []
        for kw in keywords:
            if len(kw) < 3:
                continue
            for key, value in self.database.items():
                if kw in key.split() and value not in keyword_matches:
                    keyword_matches.append(value)
                    
        if keyword_matches:
            # Return top 2 matching facts to keep results concise and high-quality
            return " | ".join(keyword_matches[:2])
            
        return f"No search results found for: '{query}'. Try refining your keywords with more specific names or metrics."


class ScrapeTool:
    """
    Simulates fetching and scraping web page text from URLs.
    Supports stateful retry logic to test agent recovery from transient network issues (HTTP 500).
    """
    def __init__(self):
        # A repository of mock website content
        self.webpages = {
            "https://flaky-database.api/data": "Data Extract: Company X metrics: Q1 Revenue = $12.5 billion, Net Margin = 18.4%, Operating Cost = $10.2 billion.",
            "https://backup-database.api/data": "Data Extract (Backup Mirror): Company X metrics: Q1 Revenue = $12.5 billion, Net Margin = 18.4%, Operating Cost = $10.2 billion.",
            "https://economics-portal.org/apple-financials": "Apple Inc. Annual Report Excerpt: Net Assets = $321.8B, Total Liabilities = $250.2B, Total Equity = $71.6B. Debt-to-Equity Ratio can be computed from these figures.",
            "https://world-stats.org/populations": "Global Demographics Summary: Tokyo Metropolitan Area population is 37.4 million. New York City population is 8.3 million. Paris City Center population is 2.1 million.",
            "https://science-history.org/turing": "Alan Turing Biographic Factsheet: Born: June 23, 1912 in London. Education: King's College, Cambridge. Known for: Decrypting the Enigma, Turing Machine, Computability Theory."
        }
        self.visit_counts = {}

    def run(self, url: str) -> str:
        url_clean = url.strip()
        
        # Standard URL validations
        if not (url_clean.startswith("http://") or url_clean.startswith("https://")):
            return "Error: Invalid URL scheme. URLs must start with 'http://' or 'https://'."

        # Initialize or increment visit counter
        self.visit_counts[url_clean] = self.visit_counts.get(url_clean, 0) + 1

        # Simulate a transient failure on the flaky endpoint on the first attempt
        if url_clean == "https://flaky-database.api/data":
            if self.visit_counts[url_clean] == 1:
                return "Error: HTTP 500 Internal Server Error - Transient database connection timeout."
        
        # Normal content retrieval
        if url_clean in self.webpages:
            return self.webpages[url_clean]
            
        # 404 Fallback
        return f"Error: HTTP 404 Page Not Found - The requested URL '{url_clean}' does not exist on this server."


class PythonREPLTool:
    """
    A safe, isolated mock Python evaluation sandbox that captures stdout and parses syntax/runtime exceptions.
    Ensures state conservation across sequential runs in the same agent context.
    """
    def __init__(self):
        # A dictionary acting as local memory/variables for the Python environment
        self.globals = {}
        self.locals = {}
        # Prepopulate useful helper libraries
        import math
        self.globals["math"] = math
        self.globals["__builtins__"] = sys.modules["builtins"]

    def run(self, code: str) -> str:
        # Preprocess code to strip block formatting if generated by an LLM (e.g. ```python ... ```)
        cleaned_code = code.strip()
        if cleaned_code.startswith("```"):
            lines = cleaned_code.splitlines()
            if lines[0].startswith("```python") or lines[0].startswith("```py"):
                cleaned_code = "\n".join(lines[1:-1])
            else:
                cleaned_code = "\n".join(lines[1:-1])
        
        # Intercept output
        stdout_buffer = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = stdout_buffer

        try:
            # We first compile the code. If there's a SyntaxError, compile will raise it.
            # Exec runs statements, capturing state changes in self.globals/self.locals
            compiled_code = compile(cleaned_code, "<sandbox_repl>", "exec")
            exec(compiled_code, self.globals, self.locals)
            
            # Reset stdout
            sys.stdout = original_stdout
            output = stdout_buffer.getvalue()
            
            # If no output was printed but the code was a single expression, we try to extract variables
            if not output.strip():
                # Check if the code was a simple variable assignment or computation we can retrieve
                lines = [l for l in cleaned_code.splitlines() if l.strip()]
                if lines:
                    last_line = lines[-1].strip()
                    # If it's a variable name, let's output its value
                    if last_line in self.locals:
                        return f"Output: {self.locals[last_line]}"
                    elif last_line in self.globals:
                        return f"Output: {self.globals[last_line]}"
                        
            return f"Execution successful.\nSTDOUT:\n{output}"
            
        except Exception as e:
            # Restore stdout
            sys.stdout = original_stdout
            
            # Extract detailed traceback just like a standard shell python process
            tb = traceback.format_exception(type(e), e, e.__traceback__)
            # Clean traceback output to be user-friendly, removing compiler frames
            clean_tb = []
            for line in tb:
                if "importlib" in line or "default_api" in line:
                    continue
                clean_tb.append(line)
            
            return f"Error: Execution failed.\nTraceback (most recent call last):\n" + "".join(clean_tb[-2:])
