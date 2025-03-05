# build with:
#
#   time docker buildx build .

FROM python:3.12-alpine

WORKDIR /app

COPY . .

RUN apk add --no-cache gcc libffi-dev musl-dev \
 && pip --root-user-action option install pipenv

RUN pipenv lock \
 && pipenv install --dev \
 && pipenv run lint

CMD ["pipenv", "run", "coverage"]
