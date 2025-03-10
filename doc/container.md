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
docker exec -it media-bridge  bash
```

----

# example output

```
$ time bin/build-container.sh
+ docker buildx build -t media-bridge-image .
[+] Building 3.5s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.05kB
 => [internal] load metadata for docker.io/library/python:3.12-alpine
...
 => => naming to docker.io/library/media-bridge-image:latest                                                                   0.0s
 => => unpacking to docker.io/library/media-bridge-image:latest                                                                0.5s

View build details: docker-desktop://dashboard/build/desktop-linux/desktop-linux/k30cujket...
+ printf '\n\n'


+ docker rm -f media-bridge
+ docker run --name media-bridge -t media-bridge-image bash -c '
    time pipenv run mb init &&
    time pipenv run mb load
'
[WARNING] Output directory does not exist, creating new directory at /app/MediaBridge/out
100%|███████████| 681204/681204 [03:35<00:00, 3162.69it/s]

real	3m45.493s
user	0m27.170s
sys	0m7.532s
100%|███████████| 17770/17770 [01:51<00:00, 159.41it/s]

101_000_000 rating rows written in 118.845 s

real    4m51.340s
user    4m15.926s
sys     0m17.315s
bin/build-container.sh  0.35s user 0.44s system 0% cpu 8:39.39 total
INFO:     Started server process [52]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```
