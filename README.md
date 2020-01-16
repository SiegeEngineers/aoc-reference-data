# aoc-reference-data

- Datasets: Game edition (The Conquerors, Wololo Kingdoms, etc)
  - Civilizations
    - Bonuses
  - Maps: Builtin maps
- Events: Community events (NAC, ECL, etc)
  - Tournaments: Specific brackets belonging to an event
    - Rounds
      - Series: A set of matches and outcome
        - Participants: Team or single individual
  - Maps: Event map pool
- Platforms: Multiplayer platforms (Voobly, VooblyCN, Aoc QQ, etc)
- Constants: Constants for match settings
- Players: Canonical names and platform ID cross references

## Sources

Event (and related) data is pulled from the [challonge](http://challonge.com) API. A list of AoC-related challonge brackets and associated events is maintained in `data/events/events.json`. Tournaments that don't have a challonge bracket are manually defined in `data/events/series.csv`.

Dataset data is generated from game data files. Code not yet included here. Datasets are numbered by their Userpatch mod identifier (0 is undefined, but selected here to represent The Conquerors).

Platform data is manually compiled.
