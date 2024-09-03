# Use a multi-stage build
FROM python:3.9-slim AS builder

# Set work directory
WORKDIR /app

# Configure apache
RUN echo 'mkdir -p /var/run/httpd' >> /root/run_apache.sh && \
 echo 'mkdir -p /var/lock/httpd' >> /root/run_apache.sh && \
 echo '/usr/sbin/httpd -D FOREGROUND' >> /root/run_apache.sh && \
 chmod 755 /root/run_apache.sh


# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies including uvicorn
RUN pip install --no-cache-dir -r requirements.txt hypercorn

# Copy the rest of the application
COPY . .

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Use a smaller base image for the final stage
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application from builder stage
COPY --from=builder /app /app

# Create the same non-root user and group in the final stage
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change ownership of the application directory
RUN chown -R appuser:appuser /app

# Use the non-root user
USER appuser

# Set Python path
ENV PYTHONPATH=/app

# Run the application using uvicorn
CMD ["hypercorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app.main:app"]
