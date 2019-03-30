"""Bootstrap reference data."""
import os
import json

import requests_cache

from aocref import model, get_metadata, list_metadata, get_class_by_tablename
from aocref import challonge


def bootstrap(session):
    """Bootstrap."""
    for filename in list_metadata('datasets'):
        dataset_id = filename.split('.')[0]
        data = json.loads(open(get_metadata(os.path.join('datasets', filename)), 'r').read())
        add_dataset(session, dataset_id, data)

    challonge_session = requests_cache.CachedSession()
    challonge_session.auth = (
        os.environ.get('CHALLONGE_USERNAME'),
        os.environ.get('CHALLONGE_KEY')
    )

    events = list(challonge.get_events(challonge_session))

    for event in events:
        add_event(session, event)

    for platform in json.loads(open(get_metadata('platforms.json'), 'r').read()):
        add_platform(session, platform)

    add_constants(session, json.loads(open(get_metadata('constants.json'), 'r').read()))

    add_event_maps(session, [event['id'] for event in events])


def add_platform(session, data):
    """Add a platform."""
    platform = model.Platform(**data)
    session.add(platform)
    session.commit()


def add_event_maps(session, event_ids):
    """Add event maps."""
    id = 0
    for event_id in list_metadata('rms'):
        if event_id not in event_ids:
            continue
        for filename in list_metadata(os.path.join('rms', event_id)):
            rms = model.EventMap(
                id=id,
                name=filename.replace('.rms', ''),
                zr=filename.startswith('ZR@'),
                event_id=event_id
            )
            session.add(rms)
            id += 1
    session.commit()


def add_event(session, data):
    """Add an event."""
    event = model.Event(id=data['id'], name=data['name'])
    session.add(event)

    for tournament_data in data['tournaments']:
        tournament = model.Tournament(
            id=tournament_data['id'],
            name=tournament_data['name'],
            event=event
        )
        session.add(tournament)
        for round_id, round_data in tournament_data['rounds'].items():
            rnd = model.Round(name=round_id, tournament=tournament)
            session.add(rnd)
            for series_data in round_data:
                series = model.Series(id=series_data['id'], played=series_data['played'], round=rnd)
                session.add(series)
                for participant_data in series_data['participants']:
                    participant = model.Participant(
                        name=participant_data['name'],
                        score=participant_data['score'],
                        winner=participant_data['winner'],
                        series=series
                    )
                    session.add(participant)
    session.commit()


def add_dataset(session, dataset_id, data):
    """Add a dataset."""
    dataset = model.Dataset(
        id=int(dataset_id),
        name=data['dataset']['name']
    )
    session.add(dataset)
    session.commit()

    for map_id, name in data['maps'].items():
        session.add(model.Map(
            id=map_id,
            dataset=dataset,
            name=name
        ))

    for civilization_id, info in data['civilizations'].items():
        civilization = model.Civilization(
            id=civilization_id,
            dataset=dataset,
            name=info['name']
        )
        session.add(civilization)
        for bonus in info['description']['bonuses']:
            session.add(model.CivilizationBonus(
                civilization_id=civilization_id,
                dataset_id=dataset_id,
                type='civ',
                description=bonus
            ))
        session.add(model.CivilizationBonus(
            civilization_id=civilization_id,
            dataset_id=dataset_id,
            type='team',
            description=info['description']['team_bonus']
        ))
        session.commit()


def add_constants(session, data):
    """Add constants."""
    for category, choices in data.items():
            cls = get_class_by_tablename(model.BASE, category)
            if not cls:
                continue
            for constant_id, constant_name in choices.items():
                constant = cls(id=constant_id, name=constant_name)
                session.add(constant)
    session.commit()
