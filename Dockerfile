FROM python:3.12-slim

# Install required packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r wyoming && useradd -r -g wyoming -s /bin/false wyoming \
    && mkdir -p /home/wyoming/.cache/huggingface/hub \
    && chown -R wyoming:wyoming /home/wyoming

# Set working directory
WORKDIR /app

# Copy and install the package
COPY requirements.txt setup.py ./
COPY wyoming_faster_whisper/ wyoming_faster_whisper/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    HF_HUB_CACHE="/home/wyoming/.cache/huggingface/hub"

# Switch to non-root user
USER wyoming

ARG MODEL="mlx-community/whisper-large-v3-turbo"
ARG LANGUAGE="it"
# Default model and language (can be overridden)
ENV MODEL="${MODEL}"
ENV LANGUAGE="${LANGUAGE}"

# Expose the default Wyoming ASR port
EXPOSE 10300

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD nc -z localhost 10300 || exit 1

# Run the server using python -m
ENTRYPOINT ["python", "-m", "wyoming_faster_whisper"]
CMD ["--model", "$MODEL", "--language", "${LANGUAGE}", "--uri", "tcp://0.0.0.0:10300"] 