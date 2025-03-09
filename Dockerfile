# build with:  bin/build-container.sh

FROM python:3.12-alpine

WORKDIR /app/MediaBridge

RUN apk update \
 && apk add --no-cache bash clang libffi-dev musl-dev nodejs openmp-dev sqlite sudo \
 && pip install --root-user-action ignore pipenv \
 && adduser -D -g '' media \
 && chown -R media:media /app \
 && echo "media ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/media \
 && chmod 0440 /etc/sudoers.d/media \
 && pwd

USER media

COPY Pipfile .

RUN sudo chown -R media:media /app \
 && pipenv lock \
 && pipenv install --dev

COPY . .

RUN sudo chown -R media:media /app

CMD ["bin/webserver-entrypoint.sh"]

# Once the webserver is running, you can execute commands like
# $ docker exec media-bridge  pipenv run lint
# $ docker exec media-bridge  pipenv run coverage
# $ docker exec -it media-bridge  bash  # gives an interactive shell prompt
