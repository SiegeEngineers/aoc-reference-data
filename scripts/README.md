# Scripts

## Import game data
The `import_game_data.py` script will read the information that can be read
from the AoE2DE installation files and patch the `data/datasets/100.json` file
with that information. The script will only print the updated JSON to standard
output, it will not actually modify the file itself.

The script has been written with the help of [uv](https://docs.astral.sh/uv) to
manage depedencies/venv. In brief, to install dependencies, and run the script:

```bash
# Install dependencies. It assumes you are in the scripts directory. This step is optional
scripts $ uv sync --script import_game_data.py

# Run the script
scripts $ uv run import_game_data.py

# To add a dependency, this how you would do it
scripts $ uv add --script import_game_data.py beautifulpackage
```

The script should automatically detect the installation location, both on
Windows and Linux, but assumes it is installed through Steam.
