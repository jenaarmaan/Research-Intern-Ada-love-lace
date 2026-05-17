import time
import json

# ANSI Color Codes for Premium Console Styling
class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Simulated World Wide Web Index
WEB_INDEX = {
    "2026 Oscar winners": [
        {
            "url": "https://variety.com/2026/oscars/winners",
            "title": "98th Academy Awards: The Complete Winners List",
            "content": "At the 98th Academy Awards (Oscars 2026), 'Dune: Part Three' dominated the night, taking home 6 Oscars including Best Director for Denis Villeneuve and Best Cinematography. The film won the most awards of any movie that evening. Christopher Nolan's biopic 'Einstein' took home 3 awards, including Best Actor."
        },
        {
            "url": "https://hollywoodreporter.com/awards/2026-oscars-sweep",
            "title": "Dune: Part Three Sweeps 2026 Oscars",
            "content": "Warner Bros' sci-fi epic 'Dune: Part Three' swept the technical categories and earned 6 statuettes at the 2026 Academy Awards. It stands out as the biggest Oscar victor of the year, leaving competitors trailing behind."
        }
    ],
    "Dune Part 3 movie budget": [
        {
            "url": "https://boxofficemojo.com/dune-part-three-financials",
            "title": "Dune: Part Three Budget and Box Office Analysis",
            "content": "Dune: Part Three carried a hefty production budget of $190 million, co-financed by Legendary Pictures and Warner Bros. It has grossed over $720 million worldwide, representing a massive financial success."
        },
        {
            "url": "https://wikipedia.org/wiki/Dune_Part_Three",
            "title": "Wikipedia: Dune: Part Three (2026 Film)",
            "content": "Dune: Part Three is a 2026 epic science fiction film. Principal photography took place on a budget of approximately $190 million USD, with filming in Jordan, Italy, and Budapest."
        }
    ]
}

class MockSearchEngine:
    """Simulates an open-world search index (Bing/Google API)."""
    @staticmethod
    def query(search_term: str) -> list[dict]:
        time.sleep(0.5)  # Simulate network latency
        # Simple lookup in our simulated web index
        normalized_query = search_term.lower()
        for indexed_term in WEB_INDEX:
            if all(word in normalized_query for word in indexed_term.lower().split()[:2]):
                return WEB_INDEX[indexed_term]
        return []

class PerplexityProSearchAgent:
    """Simulates Perplexity's multi-step information retrieval, re-planning, and synthesis loop."""
    def __init__(self):
        self.short_term_context = []
        self.episodic_memory = {}  # Tracks scraped URL contents and extracted facts
        self.citations_sources = []  # Maps citation number to URL

    def run(self, complex_query: str):
        print(f"{Color.CYAN}{Color.BOLD}[Perplexity Pro Search Initialized]{Color.END}")
        print(f"User Query: {Color.BOLD}\"{complex_query}\"{Color.END}\n")

        # 1. PERCEIVE & SEMANTIC ROUTING
        print(f"{Color.BOLD}[Step 1: Semantic Query Analysis]{Color.END}")
        print("  Analyzing query complexity...")
        time.sleep(0.6)
        
        # Reason about sub-tasks
        print("  Reasoning: \"The query asks for two connected parts: (1) The movie that won the most Oscars in 2026, and (2) that specific movie's budget. I cannot look up the budget until I discover the movie name first.\"")
        
        # 2. PLANNING: Step-by-Step Multi-Hop search
        primary_search = "2026 Oscar winners"
        print(f"  Plan: Stage 1: Search for '{primary_search}' to identify the major winner.")
        
        # 3. ACT: Execute Primary Search
        print(f"\n{Color.BOLD}[Step 2: Actuating Primary Search]{Color.END}")
        print(f"  Calling Search APIs for: {Color.YELLOW}\"{primary_search}\"{Color.END}")
        results = MockSearchEngine.query(primary_search)
        
        # 4. OBSERVE & EXTRACT (Scraping Simulation)
        print(f"  {Color.BOLD}[Observation & Scraping]{Color.END} Retrieved {len(results)} pages:")
        for res in results:
            print(f"    - Visited URL: {Color.CYAN}{res['url']}{Color.END} (Title: \"{res['title']}\")")
            # Save to episodic memory
            self.episodic_memory[res["url"]] = res["content"]
            if res["url"] not in self.citations_sources:
                self.citations_sources.append(res["url"])

        # 5. RE-EVALUATING ENVIRONMENT & DETECTING INFORMATION GAP
        print(f"\n{Color.BOLD}[Step 3: Reasoning over Extracted Facts]{Color.END}")
        extracted_winner = None
        for content in self.episodic_memory.values():
            if "Dune: Part Three" in content:
                extracted_winner = "Dune: Part Three"
                break
        
        if extracted_winner:
            print(f"  {Color.GREEN}[SUCCESS] Extracted Winner Identified:{Color.END} {Color.BOLD}{extracted_winner}{Color.END} (6 Oscars won).")
        else:
            print(f"  {Color.RED}[FAILED] Failed to identify the winner from primary search.{Color.END}")
            return

        print("  Evaluating plan: \"I have the movie name (Dune: Part Three), but I do not have its budget in my current episodic memory context.\"")
        
        # 6. DYNAMIC RE-PLANNING: Secondary Query Generation
        secondary_search = f"{extracted_winner} movie budget"
        print(f"  {Color.YELLOW}[Gap Detected]{Color.END} Generating secondary search query: {Color.BOLD}\"{secondary_search}\"{Color.END}")
        
        # 7. ACT: Execute Secondary Search
        print(f"\n{Color.BOLD}[Step 4: Actuating Secondary Search]{Color.END}")
        print(f"  Calling Search APIs for: {Color.YELLOW}\"{secondary_search}\"{Color.END}")
        secondary_results = MockSearchEngine.query(secondary_search)
        
        # 8. OBSERVE & EXTRACT
        print(f"  {Color.BOLD}[Observation & Scraping]{Color.END} Retrieved {len(secondary_results)} pages:")
        for res in secondary_results:
            print(f"    - Visited URL: {Color.CYAN}{res['url']}{Color.END} (Title: \"{res['title']}\")")
            self.episodic_memory[res["url"]] = res["content"]
            if res["url"] not in self.citations_sources:
                self.citations_sources.append(res["url"])

        # 9. FINAL SYNTHESIS & CITATION INJECTION
        print(f"\n{Color.BOLD}[Step 5: Synthesizing Final Answer]{Color.END}")
        print("  Co-referencing all collected facts into structured markdown text...")
        time.sleep(1.0)
        
        # Extracted Budget
        extracted_budget = None
        for content in self.episodic_memory.values():
            if "$190 million" in content:
                extracted_budget = "$190 million"
                break

        print(f"\n{Color.GREEN}{Color.BOLD}=== PERPLEXITY PRO ANSWER ==={Color.END}")
        
        answer = f"""At the 98th Academy Awards in 2026, the movie that won the most Oscars was **Dune: Part Three**, taking home a total of **6 Oscars** including Best Director for Denis Villeneuve and sweeping the technical categories [1][2]. 

The production budget for **Dune: Part Three** was approximately **$190 million USD** [3][4], which was co-financed by Legendary Pictures and Warner Bros. The film proved to be a major financial success, grossing over $720 million worldwide [3].

### Sources Cited:
"""
        print(answer)
        for i, url in enumerate(self.citations_sources):
            print(f" [{i+1}] {url}")
        print(f"{Color.GREEN}{Color.BOLD}============================={Color.END}\n")

if __name__ == "__main__":
    agent = PerplexityProSearchAgent()
    agent.run("Who won the most Oscars in 2026, and what was their budget?")
