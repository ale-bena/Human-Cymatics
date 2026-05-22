FROM python:3.11-slim

# SDL2 runtime libraries required for pygame import (used by viz modules)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libsdl2-2.0-0 \
        libsdl2-image-2.0-0 \
        libsdl2-mixer-2.0-0 \
        libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY crowd_mvp/ crowd_mvp/

# Headless SDL so pygame can be imported without a display
ENV SDL_VIDEODRIVER=dummy
ENV SDL_AUDIODRIVER=dummy

EXPOSE 7860

CMD ["uvicorn", "crowd_mvp.web.server:app", "--host", "0.0.0.0", "--port", "7860"]
