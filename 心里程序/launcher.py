import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def main():
    app_path = Path(__file__).with_name("app.py")
    url = "http://localhost:8501"
    webbrowser.open(url)
    time.sleep(1)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.headless",
            "true",
            "--server.port",
            "8501",
        ],
        check=False,
    )


if __name__ == "__main__":
    main()
