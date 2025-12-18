FROM python:3.12-slim

RUN useradd -m -u 1050 appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .  

USER appuser

EXPOSE 8000

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0"]

CMD ["--port", "8000"]