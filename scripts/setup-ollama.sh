#!/bin/bash
# Script to download the Ollama model after starting the container

MODEL=${OLLAMA_MODEL:-llama3.2}

echo "Waiting for Ollama to be ready..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
done

echo "Pulling model: $MODEL"
docker compose exec ollama ollama pull $MODEL

echo "Model ready!"
