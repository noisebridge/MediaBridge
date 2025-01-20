# What is MediaBridge?

MediaBridge is a project being developed at the [Noisebridge](https://github.com/noisebridge) hackerspace in San Francisco, CA, USA. See also the [Noisebridge homepage](https://www.noisebridge.net/wiki/Noisebridge) and the [wiki entry for this project](https://www.noisebridge.net/wiki/Python_Project_Meetup).

MediaBridge is in a _very_ early stage of the development. It's intended functionality is to provide recommendations that _bridge_ media types. So for example, you might say you're interested in the film _Saw_ and MediaBrige might recommend the video game _Silent Hill_ or a Stephen King book. For now, we are working on simply returning recommendations for movies, based on the [Netflix Prize dataset](https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data).

Currently, we are only accepting contributions from members of the project who meet in person at Noisebridge.

## Development

This code uses Python 3. It is tested on Python 3.12, but will probably work on versions back to 3.9.

To install the project dependencies, first install pipenv globally with `pip install pipenv`. Then create a virtual env/install dependencies with `pipenv install --dev`.

To run code in the pipenv virtual environment, prefix your command with `pipenv run` (ex. `pipenv run python` runs the python interpreter in the pipenv environment).

### Using the pipenv environment in VSCode

To fix import errors and other Intellisense features, make sure you've let VSCode know about your pipenv environment. To do that:

1. Open the VSCode command palette (Control/Command+SHIFT+P)
2. Search for and select the "Python: Select Interpreter" command
3. Choose the option that starts with `MediaBridge`

## Running code

For development purposes, you can simply run the dev script: 

```
pipenv run dev
```

Be sure to specify options such as -v and -l *before* any subcommands (process, load, etc.).  

**NOTE:** *If you encounter a ModuleNotFoundError, make sure you are in the root directory of the project, as the `mediabridge` directory is the module Pipenv is trying to reference.*

This is currently just an alias to run the main script using `pipenv run python -m mediabridge.main`, but this may change in the future, so using `pipenv run dev` will ensure the correct script is always run.

## Testing

To run unit tests,

1. Ensure `pipenv` is installed
2. Run `pipenv run test`

There is a GitHub actions "check" for passing tests, which must pass for you to be able to merge your PR.

## Code formatting

We use [ruff](https://docs.astral.sh/ruff/) for code formatting, linting, and import sorting. If you've installed the project with the instructions above, you should have access to the `ruff` binary.

The repo comes with a `.vscode` directory that contains a recommended ruff extension, as well as settings to set ruff as your Python formatter and to format code and sort imports on save. If you're not using VSCode, you can run `ruff format` from the project root directory to format all Python code.

There is a GitHub actions "check" for code formatting, which will fail if you have unformatted code in your PR.
