"""Query Liquipedia API for data updates."""
import logging
import json
import time
from collections import defaultdict

import requests
from ruamel.yaml import YAML


LOGGER = logging.getLogger(__name__)
WAIT_SECS = 30
PAGE_SIZE = 100
CONDITIONS = [
    'Category:Age of Empires II Players',
    'Is player::true'
]
PROPS = [
    'Has id',
    'Has team',
    'Has twitch stream',
    'Has youtube channel'
]


def fetch():
    """Fetch data from liquipedia API."""
    output = {}
    offset = 0
    while True:
        LOGGER.info("querying liquipedia at offset %d", offset)
        url = 'https://liquipedia.net/ageofempires/api.php'
        resp = requests.get(url, params={
            'action': 'askargs',
            'format': 'json',
            'conditions': '|'.join(CONDITIONS),
            'printouts': '|'.join(PROPS),
            'parameters': '|'.join([f'offset={offset}', f'limit={PAGE_SIZE}'])
        })

        try:
            data = resp.json()
        except json.decoder.JSONDecodeError:
            LOGGER.exception("failed to fetch: %s", resp.content)

        for result in data['query']['results'].values():
            record = result['printouts']
            team = record['Has team'][0]['fulltext'] if record['Has team'] else None
            name = record['Has id'][0]
            twitch = record['Has twitch stream'][0] if record['Has twitch stream'] else None
            youtube = record['Has youtube channel'][0] if record['Has youtube channel'] else None
            output[name] = dict(liquipedia=name, team=team, twitch=twitch, youtube=youtube)

        offset = data.get('query-continue-offset')
        if not offset:
            break
        time.sleep(WAIT_SECS)

    return output


def merge_players(results, players):
    """Merge player data."""
    for player in players:
        name = player.get('liquipedia', player['name'])
        if name not in results:
            continue
        for field in ['liquipedia', 'twitch', 'youtube', 'team']:
            if results[name][field] and not player.get(field):
                player[field] = results[name][field]


def merge_teams(results, teams, players):
    """Merge team data."""
    abbrs = {t['name']: t['abbreviation'] for t in teams}
    lookup = {p['liquipedia']: p['name'] for p in players if p.get('liquipedia')}

    by_team = defaultdict(list)
    for name, player in results.items():
        if not player.get('team'):
            continue
        if not lookup.get(name):
            continue
        by_team[player['team']].append(lookup[name])

    for team, names in by_team.items():
        yield {
            'name': team,
            'abbreviation': abbrs.get(team),
            'players': names
        }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    LOGGER.info("starting data update")
    result_data = fetch()
    yaml = YAML()
    yaml.preserve_quotes = True
    with open('data/players.yaml', 'r') as handle:
        player_data = yaml.load(handle)
    merge_players(result_data, player_data)
    with open('data/players.yaml', 'w') as handle:
        LOGGER.info("writing new players.yaml")
        yaml.dump(player_data, handle)
    with open('data/teams.json', 'r') as handle:
        team_data = json.loads(handle.read())
    with open('data/teams.json', 'w') as handle:
        LOGGER.info("writing new teams.json")
        handle.write(json.dumps(list(merge_teams(result_data, team_data, player_data)), indent=2))
    LOGGER.info("finished data update")
