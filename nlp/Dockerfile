FROM huggingface/transformers-pytorch-cpu:latest

# Set the PYTHONUNBUFFERED environment variable to prevent Python from
# buffering stdout and stderr (causing logs to not be printed in real time)
ENV PYTHONUNBUFFERED=1

# Copy the Python script to the container
COPY nlp.py /workspace/nlp.py
COPY misc.py /workspace/misc.py

# Install pymongo library
RUN pip install pymongo 

# Set the working directory
WORKDIR /workspace

# Run the Python script
CMD ["python3", "nlp.py"]
