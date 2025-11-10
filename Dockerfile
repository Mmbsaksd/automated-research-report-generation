FROM python:3.11-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .

RUN mkdir -p research_analyst_project
COPY research_and_analyst/__init__.py research_and_analyst/

RUN pip install --no-cache-dir --user -r requirements.txt

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local

COPY . .
RUN mkdir -p /app/generated_report /app/ logs
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PORT=8000



