FROM python:3.12-alpine
RUN apk add --no-cache postgresql-client
WORKDIR /work
COPY contracts/database /work/contracts/database
CMD ["python", "contracts/database/migrate.py", "up"]
