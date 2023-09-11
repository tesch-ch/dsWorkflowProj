FROM python:3.9

# Set the PYTHONUNBUFFERED environment variable to prevent Python from
# buffering stdout and stderr (causing logs to not be printed in real time)
ENV PYTHONUNBUFFERED=1

# Copy the Python script to the container
COPY app.py /flask_app/app.py
COPY templates /flask_app/templates

# Install pymongo library
RUN pip install pymongo pandas flask

# Set the working directory
WORKDIR /flask_app

# Run the Python script
CMD ["python", "app.py"]
