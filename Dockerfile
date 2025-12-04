# Use official Python 3.12 image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app
# Because I am working from another folder
COPY BackendDeveloper ./BackendDeveloper 


# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the app with uvicorn
CMD ["uvicorn", "BackendDeveloper.main:app", "--host", "0.0.0.0", "--port", "8000"]

