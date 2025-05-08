FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV RAG_API_URL=http://rag-api:8000
ENV HOST=0.0.0.0
ENV PORT=8081

EXPOSE 8081

CMD ["python", "server.py"]
