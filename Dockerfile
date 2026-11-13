FROM ghcr.io/cookiecr2nk/ts3audiobot-docker:main AS upstream

FROM ghcr.io/cookiecr2nk/ts3audiobot-docker:main
USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*

# Keep a clean copy of the upstream default configuration outside /data.
# Railway's persistent volume mounts over /data, so the startup script seeds it.
COPY --from=upstream /data/ /app/default-data/
COPY start.py /app/start.py

ENV DATA_DIR=/data \
    TS_PORT=9987 \
    BOT_NICKNAME=MusicBot \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
ENTRYPOINT ["python3", "/app/start.py"]
