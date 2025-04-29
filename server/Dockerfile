FROM python:3.12

WORKDIR /app

# Install pipx and add it to PATH
RUN pip install pipx
RUN python -m pipx ensurepath

# Install algokit using pipx
RUN pipx install algokit

# Make sure PATH includes the pipx binaries
ENV PATH="/root/.local/bin:${PATH}"

# Install your app requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your app
COPY . .

# Verify algokit is available
RUN which algokit

CMD ["python", "app.py"]