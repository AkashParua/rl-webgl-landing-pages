FROM nginx:alpine

# Submission is mounted at runtime over /usr/share/nginx/html
# Default index so the container starts even before a submission exists
RUN echo '<!DOCTYPE html><html><body><h1>No submission yet</h1></body></html>' \
    > /usr/share/nginx/html/index.html

EXPOSE 80
