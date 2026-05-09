# Root entry point — used by Pygbag to build the HTML/WASM bundle.
# For local use, run: python crowd_mvp/main.py
#
# To build for web:
#   pip install pygbag
#   pygbag .
#   Open build/web/index.html in a browser, or host the build/web/ folder anywhere.

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crowd_mvp.main import main

asyncio.run(main())
