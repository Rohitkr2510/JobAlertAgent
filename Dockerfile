FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# Apply published Debian security fixes from the base image repository.
# hadolint ignore=DL3005
RUN apt-get update \
    && apt-get upgrade --yes \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src ./src
# The local project is versioned in pyproject.toml; transitive ranges are audited by pip-audit.
# hadolint ignore=DL3013
RUN python -m pip install --no-cache-dir --upgrade 'msgpack>=1.2.1' \
    && python -m pip install --no-cache-dir '.[gmail,ui,ops]' \
    && python -m pip uninstall --yes pip setuptools
COPY config ./config
RUN useradd --system --create-home jobalert && mkdir -p data reports secrets && chown -R jobalert:jobalert /app
USER jobalert
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"
CMD ["streamlit", "run", "src/jobalert/ui.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
