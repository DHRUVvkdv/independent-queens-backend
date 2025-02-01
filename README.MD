docker build -t independent-queens-backend .
docker run --rm -p 8000:8000 --entrypoint python --env-file .env independent-queens-backend main.py
