# Use an official Python runtime as a parent image
FROM python:3.5

# Set the working directory to /app
WORKDIR /app

COPY . /app

RUN apt-get update \
        && apt-get install -y curl apt-transport-https gnupg2 \
        && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
        && curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list \
        && apt-get update \
        && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools

#RUN apt-get install krb5-user
RUN apt-get install -y gcc unixodbc-dev
# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 5000

# Run final_data_processing.py when the container launches
CMD ["python", "-u", "main.py"]