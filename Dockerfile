FROM python:3.9-slim

# Get linux dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends gcc python3-dev build-essential tzdata -y \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Set the time zone
ENV TZ=America/Santo_Domingo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set working directory
WORKDIR /usr/src/app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt --no-cache-dir

# Copy directory
COPY . /usr/src/app/

# Set default starting command
ENTRYPOINT [ "python", "-m", "playtomic_scheduler"]
