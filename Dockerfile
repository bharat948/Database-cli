FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY README.md .
COPY mongo_llm_cli/ ./mongo_llm_cli/

# Install the package
RUN pip install --no-cache-dir -e .

# Create a non-root user to run the application
RUN useradd -m appuser
USER appuser

# Create a directory for environment files
RUN mkdir -p /home/appuser/.mongo_llm
VOLUME ["/home/appuser/.mongo_llm"]

# Set the entrypoint to the mongo-llm command
ENTRYPOINT ["mongo-llm"]

# Default command (can be overridden)
CMD ["--help"] 