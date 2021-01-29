from uuid import UUID, uuid4
from datetime import date, datetime
from pydeclares import Declared, var
from pydeclares.variables import kv


class DateSerializer:
    def to_representation(self, d: date):
        return d.isoformat()

    def to_internal_value(self, string: str):
        return date.fromisoformat(string)


class DatetimeSerializer:
    def to_representation(self, d: date):
        return d.isoformat()

    def to_internal_value(self, string: str):
        return datetime.fromisoformat(string)


_datetime_ser = DatetimeSerializer()


class Court(Declared):
    date = var(date, default=date.today(), serializer=DateSerializer())
    start_time = var(datetime, serializer=_datetime_ser)
    end_time = var(datetime, serializer=_datetime_ser)


class UUIDSerializer:
    def to_representation(self, d: UUID):
        return str(d)

    def to_internal_value(self, string: str):
        return UUID(string)


class Task(Declared):
    run_id = var(UUID, default_factory=uuid4, serializer=UUIDSerializer())
    username = var(str)
    password = var(str)
    courts = kv(str, Court)
