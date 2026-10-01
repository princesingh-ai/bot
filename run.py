import argparse
import atexit
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
import uvicorn

BASE_DIR = Path(__file__).resolve().parent

def wait_for_service(host: str, port: int, process: subprocess.Popen, timeout: float = 30.0) -> bool:
    """
    Polls until the given service port is open and accepting TCP connections,
    or fails fast if the process crashes during boot.
    """
    start_time = time.time()
    backoff = 0.1
    print(f"[Orchestrator] Waiting for FastMCP readiness on {host}:{port} (timeout: {timeout}s)...")

    while time.time() - start_time < timeout:
        # Check if the subprocess crashed or exited early
        return_code = process.poll()
        if return_code is not None:
            raise RuntimeError(
                f"[Orchestrator] FastMCP server process terminated prematurely with exit code {return_code}. "
                "Check server logs and dataset files."
            )

        try:
            with socket.create_connection((host, port), timeout=0.5):
                elapsed = time.time() - start_time
                print(f"[Orchestrator] FastMCP server is ready and accepting connections ({elapsed:.2f}s).")
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(backoff)
            backoff = min(backoff * 1.4, 1.0)

    raise TimeoutError(
        f"[Orchestrator] FastMCP server did not become ready on {host}:{port} within {timeout} seconds."
    )


def main():
    parser = argparse.ArgumentParser(description="Run the CRIEYA Chatbot production/dev server.")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable uvicorn auto-reload for local development (do NOT use in production)."
    )
    args = parser.parse_args()

    # Determine configuration from environment with sensible defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    mcp_host = os.getenv("MCP_HOST", "127.0.0.1")
    mcp_port = int(os.getenv("MCP_PORT", "9000"))
    
    # Reload should only be enabled if explicitly passed via CLI or env
    reload_enabled = args.reload or os.getenv("RELOAD", "false").lower() in ("true", "1", "yes")

    print("=" * 60)
    print("  CRIEYA ASSISTANT ORCHESTRATOR")
    print(f"  FastAPI bind    : http://{host}:{port}")
    print(f"  FastMCP bind    : http://{mcp_host}:{mcp_port}")
    print(f"  Auto-reload     : {'ENABLED (Dev Mode)' if reload_enabled else 'DISABLED (Production)'}")
    print("=" * 60)

    # Prepare environment for the MCP child process
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)
    env["MCP_HOST"] = mcp_host
    env["MCP_PORT"] = str(mcp_port)

    # 1. Boot FastMCP server as a background subprocess
    print(f"[Orchestrator] Launching FastMCP server process...")
    mcp_process = subprocess.Popen(
        [sys.executable, "-m", "server.mcp_server"],
        cwd=str(BASE_DIR),
        env=env
    )

    is_shutting_down = False

    def cleanup():
        nonlocal is_shutting_down
        if is_shutting_down:
            return
        is_shutting_down = True
        print("[Orchestrator] Shutting down FastMCP server...")
        try:
            mcp_process.terminate()
            mcp_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("[Orchestrator] FastMCP did not terminate in time. Killing process...")
            mcp_process.kill()
            mcp_process.wait()
        except Exception as e:
            print(f"[Orchestrator] Error during FastMCP shutdown: {e}")
        print("[Orchestrator] Shutdown complete.")

    # Register process cleanups
    atexit.register(cleanup)

    def handle_signal(sig, frame):
        print(f"\n[Orchestrator] Received signal {sig}. Initiating clean shutdown...")
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # 2. Wait until FastMCP is truly ready before starting FastAPI
    try:
        wait_for_service(mcp_host, mcp_port, mcp_process, timeout=30.0)
    except Exception as exc:
        print(f"[Orchestrator] Startup aborted due to dependency failure: {exc}")
        cleanup()
        sys.exit(1)

    # 3. Start the FastAPI application with Uvicorn
    print(f"[Orchestrator] Starting FastAPI application on port {port}...")
    try:
        uvicorn.run("app.main:app", host=host, port=port, reload=reload_enabled)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
