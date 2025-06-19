FROM python:3.11

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install system dependencies including distutils
RUN apt-get update && \
    apt-get install -y python3-distutils build-essential && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port Flask uses
EXPOSE 5000

# Start your Flask app
CMD ["python", "app.py"]
