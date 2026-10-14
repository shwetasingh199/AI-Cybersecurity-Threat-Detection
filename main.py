from pathlib import Path
import sys
import streamlit.web.cli as stcli

if __name__ == "__main__":
    app = Path(__file__).parent / "app" / "dashboard.py"
    sys.argv = ["streamlit", "run", str(app)]
    raise SystemExit(stcli.main())
