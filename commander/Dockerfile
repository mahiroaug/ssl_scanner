# Base image
FROM python:3.9

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && apt-get -y install docker.io

RUN pip install --upgrade pip

# Install necessary libraries
RUN pip install mysql-connector-python
RUN pip install docker


# Copy the code to the container
COPY commander.py /app/commander.py

# Set working directory
WORKDIR /app

# Run the Python script
ENTRYPOINT ["python", "commander.py"]