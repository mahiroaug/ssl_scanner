# Base image
FROM python:3.9

ARG MYSQL_ROOT_PASSWORD
ARG TZ

RUN apt-get update && apt-get install -y --no-install-recommends
RUN pip install --upgrade pip

# Install necessary libraries
RUN pip install requests cryptography
RUN pip install pyopenssl
RUN pip install mysql-connector-python

# Copy the code to the container
COPY ssl_certificate_checker.py /app/ssl_certificate_checker.py
COPY update.py /app/update.py

# Set working directory
WORKDIR /app

ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
ENV TZ=${TZ}

# Run the Python script
ENTRYPOINT ["python", "update.py"]