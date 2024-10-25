# What is MediaBridge?

MediaBridge is a project being developed at the [Noisebridge](https://github.com/noisebridge) hackerspace in San Francisco, CA, USA. See also the [Noisebridge hompage](https://www.noisebridge.net/wiki/Noisebridge) and the [wiki entry for this project](https://www.noisebridge.net/wiki/Python_Project_Meetup).

MediaBridge is in a _very_ early stage of the development. It's intended functionality is to provide recommendations that _bridge_ media types. So for example, you might say you're interested in the film _Saw_ and MediaBrige might recommend the video game _Silent Hill_ or a Stephen King book. For now, we are working on simply returning recommendations for movies, based on the [Netflix Prize dataset](https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data).

Currently, we are only accepting contributions from members of the project who meet in person at Noisebridge.

## Development

This code uses Python 3, probably at least 3.9.

To install the project dependencies, first install pipenv globally with `pip install pipenv`. Then create a virtual env/install dependencies with `pipenv install`.

To run code in the project, prefix your command with `pipenv run`, a la `pipenv run python -m mediabridge.main`.

## Testing

To run unit tests,

1. Ensure `pipenv` is installed
2. Run `pipenv run pytest`
