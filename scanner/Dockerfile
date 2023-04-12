# Base image
FROM python:3.10

RUN apt-get update && apt-get install -y --no-install-recommends
RUN pip install --upgrade pip

# Install necessary libraries
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# Copy the code to the container
COPY \
  ssl_certificate_checker.py \
  controler.py \
  db.py \
  push_slackbot.py \
  command.py \
  command_util.py \
  __main__.py \
  /app/

# Add test codes
COPY ./tests /app/tests
COPY ./migration_tests /app/migration_tests

# Set working directory
WORKDIR /app

# Run the Python script
#ENTRYPOINT ["python", "controler.py", "3", "1"]
ENTRYPOINT ["python","."]
