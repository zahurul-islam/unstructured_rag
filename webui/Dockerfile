FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV RAG_API_URL=http://rag-api:8000
ENV HOST=0.0.0.0
ENV PORT=8080

EXPOSE 8080

CMD ["python", "server.py"]
