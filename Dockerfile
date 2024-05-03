FROM python:3.12.2  # Base image with Python 3.12

WORKDIR /speech_assistant_tuto  # Working directory within the container

COPY requirements.txt ./  # Copy requirements file
RUN pip install -r requirements.txt  # Install dependencies

COPY . .  # Copy your project code to the working directory

CMD ["python", "your_script.py"]  # Command to run your LLM script
