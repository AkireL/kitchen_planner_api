FROM python:3.11-slim

WORKDIR /app/

# Create a group in the system and a user associated with that group
RUN groupadd -r admingroup && useradd -r -g admingroup leouser
RUN chown -R leouser:admingroup /app/

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

USER leouser

EXPOSE 8000