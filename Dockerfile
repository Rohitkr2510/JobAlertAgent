FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir '.[gmail]'
COPY config ./config
RUN useradd --system --create-home jobalert && mkdir -p data reports secrets && chown -R jobalert:jobalert /app
USER jobalert
ENTRYPOINT ["jobalert"]
CMD ["--help"]
