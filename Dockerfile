# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the image
COPY . .

# Expose the port the app will run on
EXPOSE 7860

# Command to run the application
CMD gunicorn --bind 0.0.0.0:7860 app:app