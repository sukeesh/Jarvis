FROM python:3.6-slim-jessie

COPY . /app
WORKDIR /app

ENV JARVIS_PATH /usr/local/bin/jarvis
RUN pip3 install --upgrade -r requirements.txt && \
    echo "python3 /app/jarviscli/" > "$JARVIS_PATH" && \
    chmod +x "$JARVIS_PATH" && \
    python -m nltk.downloader -d jarviscli/data/nltk wordnet

ENTRYPOINT "/bin/sh" "$JARVIS_PATH"
