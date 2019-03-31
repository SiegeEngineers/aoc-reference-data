"""AoC reference data table model."""

# pylint: disable=too-few-public-methods

from sqlalchemy import (
    Boolean, DateTime, Column, UnicodeText,
    ForeignKey, Integer, String, ForeignKeyConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


BASE = declarative_base()


class Platform(BASE):
    """Multiplayer platform."""
    __tablename__ = 'platforms'
    id = Column(String, primary_key=True)
    name = Column(String)
    url = Column(String)
    match_url = Column(String)


class Event(BASE):
    """Event (one or more tournaments)."""
    __tablename__ = 'events'
    id = Column(String, primary_key=True)
    name = Column(String)


class Tournament(BASE):
    """A specific tournament (or stage of an event)."""
    __tablename__ = 'tournaments'
    id = Column(String, primary_key=True)
    name = Column(String)
    event_id = Column(String, ForeignKey('events.id'))
    event = relationship('Event', foreign_keys=[event_id], backref='tournaments')


class Round(BASE):
    """Tournament round."""
    __tablename__ = 'rounds'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tournament_id = Column(String, ForeignKey('tournaments.id'))
    tournament = relationship('Tournament', foreign_keys=[tournament_id], backref='rounds')


class Series(BASE):
    """Series of matches."""
    __tablename__ = 'series'
    id = Column(String, primary_key=True)
    round_id = Column(Integer, ForeignKey('rounds.id'))
    round = relationship('Round', foreign_keys=[round_id], backref='series')
    played = Column(DateTime)
    tournament = relationship(
        'Tournament',
        secondary='rounds',
        primaryjoin='Series.round_id == Round.id',
        secondaryjoin='Tournament.id == Round.tournament_id',
        viewonly=True,
        uselist=False
    )


class Participant(BASE):
    """Series participants (team or single player)."""
    __tablename__ = 'participants'
    id = Column(Integer, primary_key=True)
    series_id = Column(String, ForeignKey('series.id'))
    series = relationship('Series', foreign_keys=[series_id], backref='participants')
    name = Column(String)
    score = Column(Integer)
    winner = Column(Boolean)


class Dataset(BASE):
    """AoC Dataset (a specific set of civs/balance/etc)."""
    __tablename__ = 'datasets'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Civilization(BASE):
    """Civilization belonging to a dataset."""
    __tablename__ = 'civilizations'
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), primary_key=True)
    dataset = relationship('Dataset', foreign_keys=[dataset_id])
    name = Column(String, nullable=False)


class CivilizationBonus(BASE):
    """Bonus belonging to civilization."""
    __tablename__ = 'civilization_bonuses'
    id = Column(Integer, primary_key=True)
    civilization_id = Column(Integer)
    dataset_id = Column(Integer, ForeignKey('datasets.id'))
    type = Column(String)
    description = Column(String)
    civilization = relationship(
        'Civilization',
        foreign_keys=[civilization_id, dataset_id],
        backref='bonuses'
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ['civilization_id', 'dataset_id'], ['civilizations.id', 'civilizations.dataset_id']
        ),
    )


class EventMap(BASE):
    """Event map."""
    __tablename__ = 'event_maps'
    id = Column(Integer, primary_key=True)
    event_id = Column(String, ForeignKey('events.id'))
    event = relationship('Event', foreign_keys=event_id, backref='maps')
    name = Column(String)
    zr = Column(Boolean)
    aoe2mapnet_id = Column(String)


class Map(BASE):
    """Builtin map."""
    __tablename__ = 'maps'
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), primary_key=True)
    dataset = relationship('Dataset', foreign_keys=[dataset_id])
    name = Column(String)


class GameType(BASE):
    """Game type."""
    __tablename__ = 'game_types'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class StartingResources(BASE):
    """Starting resoruces."""
    __tablename__ = 'starting_resources'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class VictoryCondition(BASE):
    """ictory conditions."""
    __tablename__ = 'victory_conditions'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class MapRevealChoice(BASE):
    """Map reveal choices."""
    __tablename__ = 'map_reveal_choices'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class StartingAge(BASE):
    """Starting Ages."""
    __tablename__ = 'starting_ages'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Difficulty(BASE):
    """Difficulties."""
    __tablename__ = 'difficulties'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Speed(BASE):
    """Speeds."""
    __tablename__ = 'speeds'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class MapSize(BASE):
    """Map sizes."""
    __tablename__ = 'map_sizes'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class PlayerColor(BASE):
    """Player color."""
    __tablename__ = 'player_colors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
