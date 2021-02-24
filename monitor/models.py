from uuid import UUID, uuid4
from datetime import date, datetime, timedelta
from pydeclares import Declared, var
from pydeclares.variables import vec


class DateSerializer:
    def to_representation(self, d: date):
        return d.isoformat()

    def to_internal_value(self, string: str):
        return date.fromisoformat(string)


class TimedeltaSerde:
    def to_representation(self, d: timedelta):
        o = datetime.min + d
        return o.strftime("%H:%M")

    def to_internal_value(self, timestr: str):
        dt = datetime.strptime(timestr, "%H:%M")
        return timedelta(hours=dt.hour, minutes=dt.minute)


_timedelta_serde = TimedeltaSerde()


class Court(Declared):
    num = var(int, required=False)
    name = var(str, required=False)
    date = var(date, default=date.today(), serializer=DateSerializer())
    start_time = var(timedelta, serializer=_timedelta_serde)
    end_time = var(timedelta, serializer=_timedelta_serde)

    def __post_init__(self, **omits):
        if self.num is None and self.name is None:
            raise ValueError("num or name is required for court")


class UUIDSerializer:
    def to_representation(self, d: UUID):
        return str(d)

    def to_internal_value(self, string: str):
        return UUID(string)


class Task(Declared):
    run_id = var(UUID, default_factory=uuid4, serializer=UUIDSerializer())
    username = var(str)
    password = var(str)
    courts = vec(Court)
