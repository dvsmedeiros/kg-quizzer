# cohmetrix
FROM ubuntu:focal

ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies including those needed for h5py and other C extensions
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        default-jre \
        build-essential \
        python3-dev \
        pkg-config \
        libhdf5-dev \
        # libpq-dev # For compiling psycopg2 from source, but psycopg2-binary is used below
        # libxml2-dev libxslt1-dev # If lxml needs to be compiled and wheels aren't found
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools
RUN pip3 install --upgrade pip setuptools

WORKDIR /opt/text_metrics

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install psycopg2-binary (often has fewer system dependencies than compiling psycopg2)
RUN pip3 install psycopg2-binary

RUN pip3 install "numpy~=1.19.5"

# Install packages from requirements.txt
# This is where h5py will be built, now with necessary system libs
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# If nlpnet is in requirements.txt, this line might be redundant.
# Otherwise, ensure its dependencies are met by requirements.txt or system packages.
# RUN cd tools/nlpnet-py3 && python3 setup.py install && cd ..

# Download NLTK data after NLTK is installed
RUN python3 -m nltk.downloader all

# Install local tool idd3 after its dependencies are installed via requirements.txt
RUN cd tools/idd3 && python3 setup.py install

# WORKDIR /opt/text_metrics # Already set

# Set a default command (optional, replace with your actual application command)
# CMD ["python3", "your_main_script.py"]