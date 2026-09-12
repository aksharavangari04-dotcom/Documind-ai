FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project code
COPY client/ .

EXPOSE 10000

# Run Streamlit on Render port
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]
