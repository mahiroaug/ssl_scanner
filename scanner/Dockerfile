# Base image
FROM python:3.9

RUN apt-get update && apt-get install -y --no-install-recommends
RUN pip install --upgrade pip

# Install necessary libraries
RUN pip install requests cryptography
RUN pip install pyopenssl
RUN pip install mysql-connector-python

# Copy the code to the container
COPY ssl_certificate_checker.py /app/ssl_certificate_checker.py
### obsolete
#COPY update.py /app/update.py
COPY controler.py /app/controler.py
COPY db_handler.py /app/db_handler.py

# Set working directory
WORKDIR /app

# Run the Python script
ENTRYPOINT ["python", "controler.py"]