# build with:   docker buildx build -t media-bridge .
# run with:     docker run -it media-bridge

FROM python:3.12-alpine

WORKDIR /app/MediaBridge

RUN apk update \
 && apk add --no-cache bash clang libffi-dev musl-dev nodejs openmp-dev sudo \
 && pip install --root-user-action ignore pipenv \
 && adduser -D -g '' media \
 && chown -R media:media /app \
 && echo "media ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/media \
 && chmod 0440 /etc/sudoers.d/media \
 && pwd

ENV PATH="/app/MediaBridge:${PATH}"

USER media

COPY . .

RUN sudo chown -R media:media /app \
 && pipenv lock \
 && pipenv install --dev \
 && pipenv run coverage  > /tmp/coverage.log

CMD ["/bin/bash", "-i"]
