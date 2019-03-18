"""Challonge integration."""

import csv
import json
import logging
from collections import defaultdict

import iso8601

from aocref import get_metadata


LOGGER = logging.getLogger(__name__)
EVENT_DATA = json.loads(open(get_metadata('events/events.json'), 'r').read())
SERIES_DATA = list(csv.DictReader(filter(lambda row: row[0] not in ['#', '\n'],
                                         open(get_metadata('events/series.csv'), 'r'))))
CHALLONGE_API_URL = 'https://api.challonge.com/v1/tournaments/{}.json'
STATE_PENDING = 'pending'
SCORE_SEPARATOR_1 = ','
SCORE_SEPARATOR_2 = '-'


def _map_participants(participant_data):
    """Map participant IDs to names."""
    participants = {}
    for participant_wrapper in participant_data:
        participant = participant_wrapper['participant']

        # Record group stage name, if applicable
        if len(participant['group_player_ids']) == 1:
            pid = participant['group_player_ids'][0]
            participants[pid] = participant['name']

        pid = participant['id']
        participants[pid] = participant['name']
    return participants


def _compute_total_score(scores_csv):
    """Compute total score per particpant.

    Some tournament admins report scores per match in a series,
    but not all. Therefore, we have to return the lowest common
    denominator - total score for the series (challonge "match").
    """
    total_score = [0, 0]
    for score in scores_csv.split(SCORE_SEPARATOR_1):
        parts = score.split(SCORE_SEPARATOR_2)
        if len(parts) == 2:
            total_score[0] += int(parts[0])
            total_score[1] += int(parts[1])
    return total_score


def _format_participants(match, participants, total_score):
    """Format participants as list."""
    return [{
        'id': match[id_field],
        'name': participants.get(match[id_field]),
        'score': total_score[i],
        'winner': match['winner_id'] == match[id_field]
    } for i, id_field in enumerate(['player1_id', 'player2_id'])]


def _get_manual_tournament(tournament_id):
    """Get manually-entered data for a tournament."""
    rounds = defaultdict(list)
    for row in SERIES_DATA:
        if row['tournament_id'] == tournament_id:
            total_score = _compute_total_score(row['score'])
            rounds[row['round_id']].append({
                'id': '{}-{}-{}'.format(tournament_id, row['round_id'], row['series_id']),
                'played': iso8601.parse_date(row['played']),
                'participants': [{
                    'id': None,
                    'name': name,
                    'score': total_score[i],
                    'winner': max(total_score) == total_score[i]
                } for i, name in enumerate([row['p1'], row['p2']])]
            })

    name = None
    for event in EVENT_DATA:
        for tournament in event['tournaments']:
            if isinstance(tournament, list) and tournament[0] == tournament_id:
                name = tournament[1]

    if name:
        return {
            'id': tournament_id,
            'name': name,
            'rounds': rounds
        }
    return None


def get_tournament(session, tournament_id):
    """Get round and participant data for a tournament."""

    manual = _get_manual_tournament(tournament_id)
    if manual:
        LOGGER.debug("falling back to manual data for %s (no Challonge bracket)", tournament_id)
        return manual

    data = session.get(CHALLONGE_API_URL.format(tournament_id), params={
        'include_matches': 1,
        'include_participants': 1
    }).json()

    tournament = data.get('tournament')
    participants = _map_participants(tournament['participants'])
    rounds = defaultdict(list)

    for match_wrapper in tournament['matches']:
        match = match_wrapper.get('match')
        if match['state'] != STATE_PENDING:
            total_score = _compute_total_score(match['scores_csv'])
            round_key = '{};{}'.format(match['round'], match['group_id'] or 0)
            rounds[round_key].append({
                'id': match['id'],
                'participants': _format_participants(match, participants, total_score),
                'played': iso8601.parse_date(match['updated_at'])
            })
    return {
        'id': tournament_id,
        'name': tournament['name'],
        'rounds': rounds
    }


def get_events(session):
    """Get event data."""
    for event in EVENT_DATA:
        tournaments = []
        for tournament_id in event['tournaments']:
            if isinstance(tournament_id, list):
                tournament_id = tournament_id[0]
            tournaments.append(get_tournament(session, tournament_id))
        yield {
            'id': event['id'],
            'name': event['name'],
            'tournaments': tournaments
        }
