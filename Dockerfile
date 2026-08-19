FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir '.[gmail,ui]'
COPY config ./config
RUN useradd --system --create-home jobalert && mkdir -p data reports secrets && chown -R jobalert:jobalert /app
USER jobalert
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"
CMD ["streamlit", "run", "src/jobalert/ui.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
