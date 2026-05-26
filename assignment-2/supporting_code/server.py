import http.server
import socketserver
import json
import os
import webbrowser
import threading
import time
from urllib.parse import urlparse, parse_qs
from agent import ReActAgent

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class ReActAgentHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/run':
            # Handle ReAct Agent Execution
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
                task = payload.get('task', '')
                
                if not task:
                    self.send_error_response(400, "Task query parameter 'task' is required.")
                    return
                
                # Execute agent
                agent = ReActAgent()
                result = agent.run(task)
                
                # Respond with trace logs and metrics
                self.send_json_response(result)
            except Exception as e:
                self.send_error_response(500, f"Internal server error: {str(e)}")
        else:
            self.send_error_response(404, "Endpoint not found.")

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/api/default_tests':
            # Expose default benchmark cases
            default_cases = [
                {
                    "id": "task_1",
                    "name": "Multi-Hop Financial Query",
                    "prompt": "Find Apple's 2024 annual revenue and Microsoft's 2024 annual revenue, and calculate the absolute difference between them."
                },
                {
                    "id": "task_2",
                    "name": "Flaky Scraper Recovery",
                    "prompt": "Scrape financial statistics from the URL 'https://flaky-database.api/data' and recover using backup mirror endpoints if a failure occurs."
                },
                {
                    "id": "task_3",
                    "name": "Buggy Code Runtime Correction",
                    "prompt": "Calculate the result of dividing 100 by the divisor variable (initially 0). Catch standard runtime exceptions (ZeroDivisionError) and correct it to divisor=5."
                },
                {
                    "id": "task_4",
                    "name": "Recursive Demographic Analysis",
                    "prompt": "Search for the individual populations of Paris, Tokyo, and New York City, and calculate their mathematical average population using python."
                },
                {
                    "id": "task_5",
                    "name": "Missing Tool Input Query Refinement",
                    "prompt": "Search for Google's 2024 annual revenue, handling an empty search string error initially, and recover using refined keywords."
                }
            ]
            self.send_json_response(default_cases)
        else:
            # Let simple HTTP request handler serve static index.html, index.css, index.js files
            super().do_GET()

    def send_json_response(self, data, status_code=200):
        try:
            response_bytes = json.dumps(data).encode('utf-8')
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_bytes)))
            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response_bytes)
        except Exception as e:
            print(f"Error sending response: {e}")

    def send_error_response(self, status_code, message):
        self.send_json_response({"error": message}, status_code=status_code)

    def log_message(self, format, *args):
        # Suppress noise in stdout but log key actions
        print(f"[SERVER] {format % args}")

def open_browser():
    time.sleep(1.2) # Allow port binding to finalize
    url = f"http://localhost:{PORT}"
    print(f"[SERVER] Launching default browser automatically at: {url}")
    webbrowser.open(url)

def run_server():
    # Allow port reuse to prevent address-already-in-use errors
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ReActAgentHandler) as httpd:
        print(f"[SERVER] Running HTTP server at: http://localhost:{PORT}")
        print(f"[SERVER] Root workspace directory: {DIRECTORY}")
        
        # Start browser trigger thread
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVER] Server stopped by user request.")
        except Exception as e:
            print(f"[SERVER] Server error: {e}")

if __name__ == "__main__":
    run_server()
