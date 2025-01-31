FROM python:3.11-slim

WORKDIR /game_update_notifier

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "game_update_notifier.py"]
