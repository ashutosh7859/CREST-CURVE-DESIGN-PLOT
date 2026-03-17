# start.py  (place in the same folder as your main app script)

import os
import subprocess

# ── Only change this line when you want to switch the entry file ──
MAIN_SCRIPT = "Vertical Curves Design and Review.py"   # ← your current file
# or later: "app.py"  or "pages/01_Home.py"  etc.

# You can also make it dynamic from environment variable if you ever want
# MAIN_SCRIPT = os.getenv("STREAMLIT_MAIN", "Vertical Curves Design & Review.py")

subprocess.run(
    [
        "streamlit", "run",
        MAIN_SCRIPT,
        "--server.port", os.getenv("PORT", "8501"),
        "--server.address", "0.0.0.0",
        # Optional extras you might want later:
        # "--server.headless", "true",
        # "--browser.serverAddress", "0.0.0.0",
    ],
    check=True
)