echo -e "======== Docker build ========"
docker build -t likeca/django . -f Dockerfile
docker push likeca/django:latest
echo -e "======== End of docker build ========\n"

echo -e "======== Docker compose up ========"
# docker start django
# docker compose up -d
echo -e "======== End of docker compose up ========\n"

