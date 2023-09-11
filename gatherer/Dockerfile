FROM python:latest

# Copy the Python script to the container
COPY gather.py /app/gather.py

# Install pymongo and newspaper3k libraries
RUN pip install pymongo newspaper3k

# Set the working directory
WORKDIR /app

# Run the Python script
CMD ["python", "gather.py"]
