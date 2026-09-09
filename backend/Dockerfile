# Use the official Python image
FROM python:3.12-slim 

# Set the working directory inside the container
WORKDIR /app

# Copying requirements and app into /app
COPY requirements.txt .
# We seprate it to avoid downloading dependcy again and again
#  fullstop in requiremnts.txt seprate souce from destination if u leave . alone then the destiantion is workdir

# Run - To install reqs
RUN pip install -r /app/requirements.txt

# Copying app into app
COPY app ./app

# Expose
EXPOSE 8000

#CMD
CMD ["uvicorn","app.main:app", "--host", "0.0.0.0", "--port", "8000"]