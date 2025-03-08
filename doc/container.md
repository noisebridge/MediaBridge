# running within a container

Team members may develop on diverse operating systems,
e.g. on a MacOS or Windows (WSL2) laptop.
It is possible to trigger varying behavior based on OS.
When reproducing behavior in order to diagnose a bug,
it can be helpful to put everyone on the same page,
running the same Alpine Linux OS.

The Docker
[documentation](https://docs.docker.com/get-started/get-docker/)
explains how to obtain and run the Docker Desktop app.
You will want to see it running in your task bar
when you're working with containers.

To build a container from a cloned repo, cd to top-level MediaBridge and run
```
bin/build-container.sh
```
This should complete within ~ ten minutes.
Longer if downloaded files are not yet cached.

Please refer to comments in the
[Dockerfile](https://github.com/noisebridge/MediaBridge/blob/main/Dockerfile)
for ways to use the resulting image.
For example you can get a bash prompt using
```
docker run -it -p 8001:8001 media-bridge
```
