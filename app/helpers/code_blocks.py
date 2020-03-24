# -*- coding: utf-8 -*-

from emmett import Injector


_nutshell = """
from emmett import App, request, response
from emmett.orm import Database, Model, Field
from emmett.tools import service

class TimeTravel(Model):
    traveler = Field.string()
    returned = Field.bool(default=False)

app = App(__name__)
db = Database(app)
db.define_models(TimeTravel)
app.pipeline = [db.pipe]

@app.route(methods='get')
@service.json
async def completed_travels():
    page = request.query_params.page or 1
    travels = TimeTravel.where(
        lambda t: t.returned == True
    ).select(paginate=(page, 20))
    return {'travels': travels}"""

_async = """
from emmett import websocket

@app.websocket()
async def time_travels():
    channel = await mypubsub.subscribe(
        "channel:time_travels"
    )
    await websocket.accept()

    while True:
        async for travel in channel.iter():
            await websocket.send(travel)"""

_orm_relations_old = """
from emmett.orm import Model, Field, has_many, belongs_to

class User(Model):
    has_many('posts')
    email = Field.string()

    validation = {
        'email': {'is': 'email'}
    }

class Post(Model):
    belongs_to('user')
    body = Field.text()

    validation = {
        'body': {'presence': True}
    }"""

_orm_relations = """
from emmett.orm import Model, has_many, belongs_to

class Passenger(Model):
    has_many('time_travels')

class Position(Model):
    has_many(
        {'departures': 'TimeTravel.source'},
        {'arrivals': 'TimeTravel.destination'},
        {'travelers': 'TimeTravel.passenger'}
    )

class TimeTravel(Model):
    belongs_to(
        'passenger',
        {'source': 'Position'},
        {'destination': 'Position'}
    )
"""

_orm_aggregation = """
class Event(Model):
    location = Field.string()
    happens_at = Field.datetime()

events_count = Event.id.count()
db.where(
    Event.happens_at.year() == 1955
).select(
    Event.location,
    events_count,
    groupby=Event.location,
    orderby=~events_count,
    having=(events_count > 10))"""

_templates = """
{{ extend 'layout.html' }}

<div class="time-travels">
  {{ for idx, travel in enumerate(travels): }}
  {{ style_class = "gray" if idx % 2 else "light" }}
  <div class="travel {{ =style_class }}">
    <h2>{{ =travel.destination }}</h2>
  </div>
  {{ pass }}

  {{ if not travels: }}
  <div>
    <em>No time travels so far.</em>
  </div>
  {{ pass }}
</div>"""


class CodeBlocks(Injector):
    namespace = "code_blocks"

    nutshell = _nutshell
    async_code = _async
    orm_relations = _orm_relations
    orm_aggregation = _orm_aggregation
    templates = _templates
