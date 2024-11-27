# Ubuntu, because that's where I developed it.
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libsystemd-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Step 2: Set the working directory in the container
WORKDIR /backend

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install fastapi uvicorn "fastapi[standard]"


# Step 5: Copy the FastAPI application code into the container
COPY . .

# Step 6: Expose the port that FastAPI will run on
EXPOSE 8000

# Step 7: Define the command to run the application using uvicorn
CMD ["fastapi", "run", "src/main.py"]
