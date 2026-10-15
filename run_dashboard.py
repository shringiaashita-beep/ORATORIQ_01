"""
Single-command launcher for Ragas Evaluation Studio.

Starts the FastAPI server with:
- Configurable host and port via CLI arguments (--host, --port, --no-browser)
- Early port availability validation with actionable conflict diagnostics
- Background readiness waiter that opens the browser only after the server is healthy
"""

import sys
import time
import socket
import argparse
import threading
import webbrowser
import urllib.request
import uvicorn

def is_port_in_use(host: str, port: int) -> bool:
    """Checks whether the specified port is already bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0

def wait_for_server_and_open_browser(url: str, timeout_sec: int = 12):
    """Polls /api/health until server responds, then opens the browser."""
    health_url = f"{url}/api/health"
    start_time = time.time()
    
    while time.time() - start_time < timeout_sec:
        try:
            req = urllib.request.Request(health_url, headers={"User-Agent": "RagasStudioLauncher"})
            with urllib.request.urlopen(req, timeout=1.0) as response:
                if response.status == 200:
                    print(f"\n[Launcher] Server verified healthy at {health_url}. Opening browser...\n")
                    webbrowser.open(url)
                    return
        except Exception:
            time.sleep(0.4)
            
    print(f"\n[Launcher] Note: Could not verify server health within {timeout_sec}s. Please navigate to {url} manually.")

def main():
    parser = argparse.ArgumentParser(description="Launch Ragas Evaluation Studio")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser")
    parser.add_argument("--reload", action="store_true", help="Enable hot reload for development")
    args = parser.parse_args()

    print("=" * 72)
    print("  ORATORIQ — EVIDENCE-BASED SPEECH COACH")
    print("  Physical Acoustics • 52-Pair Contrastive Corpus • Versioned Rubrics")
    print("=" * 72)

    url = f"http://{args.host}:{args.port}"

    if is_port_in_use(args.host, args.port):
        print(f"\n[ERROR] Port {args.port} is already in use on {args.host}!")
        print(f"Another application or existing OratorIQ instance is running on this port.")
        print(f"Suggestions:")
        print(f"  1. Terminate the existing process running on port {args.port}")
        print(f"  2. Or launch on a different port: python run_dashboard.py --port {args.port + 1}\n")
        sys.exit(1)

    print(f"\nStarting OratorIQ Speech Coaching Platform on {url}")
    print(f"API Documentation available at: {url}/docs")
    print(f"Interactive Speech Studio available at: {url}/\n")

    if not args.no_browser:
        waiter_thread = threading.Thread(
            target=wait_for_server_and_open_browser,
            args=(url,),
            daemon=True
        )
        waiter_thread.start()

    try:
        uvicorn.run(
            "ragas_dashboard.backend.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[Launcher] Gracefully shutting down Ragas Evaluation Studio. Goodbye!")

if __name__ == "__main__":
    main()
