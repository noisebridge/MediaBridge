# build with:   docker buildx build -t media-bridge .
# run with:     docker run -it media-bridge

FROM python:3.12-alpine

WORKDIR /app

COPY . .

RUN apk add --no-cache bash gcc libffi-dev musl-dev \
 && pip install --root-user-action ignore pipenv

CMD ["/bin/bash", "-i"]

#RUN pipenv lock \
# && pipenv install --dev \
# && pipenv run lint

#CMD ["pipenv", "run", "coverage"]
