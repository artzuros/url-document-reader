# Base image
FROM python:3.10
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script to the working directory
COPY app.py .

# Set the command to run your web application with Streamlit
CMD ["streamlit", "run", "--server.port", "80", "app.py"]
