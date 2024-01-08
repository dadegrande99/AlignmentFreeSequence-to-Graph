# Set the base image
FROM python:3.10


# Install the necessary packages for GUI applications
RUN apt-get update && apt-get install -y \
    python3-tk

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory in the container
ADD . .

# Command to run on container start
CMD [ "python", "interface.py" ]

# Neo4j service
FROM neo4j:latest

# Set environment variables for Neo4j
ENV NEO4J_AUTH=neo4j/testtest1

# Expose Neo4j HTTP and Bolt ports
EXPOSE 7474 7687