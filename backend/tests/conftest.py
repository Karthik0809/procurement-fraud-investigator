import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("NVIDIA_API_KEY", "")  # tests always run offline
os.environ.setdefault("DATA_BACKEND", "local")
