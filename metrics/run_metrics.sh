#!/bin/bash

# Define the host path for metrics output
# Ensure this directory exists on your Mac: /Users/gabrielleite/Backup/QA-Promp-KG/nilcmetrix/metrics_output
HOST_METRICS_OUTPUT_PATH="/Users/gabrielleite/Backup/QA-Promp-KG/qa-prompt-kg/metrics/data"

# Create the host directory if it doesn't exist (optional, but good practice for scripts)
mkdir -p "$HOST_METRICS_OUTPUT_PATH"

docker run --rm \
    --link pgs_cohmetrix:pgs_cohmetrix \
    -v "/Users/gabrielleite/Backup/QA-Promp-KG/nilcmetrix:/opt/text_metrics" \
    -v "/Users/gabrielleite/Backup/QA-Promp-KG/qa-prompt-kg/resultado:/opt/resultados" \
    -v "$HOST_METRICS_OUTPUT_PATH:/opt/metrics/data" \
    cohmetrix:focal \
    bash -c "python3 -u final_metrics.py" # Adicione o -u aqui