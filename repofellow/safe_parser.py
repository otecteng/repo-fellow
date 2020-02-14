from sqlalchemy.orm.attributes  import InstrumentedAttribute
from sqlalchemy import inspect
from sqlalchemy.sql.sqltypes import DateTime,String
import datetime
import logging


class Convertor:
    mapping = {}

    @classmethod
    def load_schema(cls,x):
        inst = inspect(type(x))
        fields = {}
        for c_attr in inst.mapper.column_attrs:
            for i in c_attr.columns:
                fields[i.name] = i.type
        cls.mapping[type(x)] = fields

    @classmethod
    def json2db(cls,data,obj,key,field = None):
        if key not in data or data[key] is None:
            logging.info("{} not exist in data".format(key))
            return
        if type(obj) in cls.mapping:
            fields = cls.mapping[type(obj)]
        else:
            inst = inspect(type(obj))
            fields = {}
            for c_attr in inst.mapper.column_attrs:
                for i in c_attr.columns:
                    fields[i.name] = i.type
            cls.mapping[type(obj)] = fields

        if field is None:
            field = key

        field_type = fields[field]
        if isinstance(field_type,DateTime):
            setattr(obj,field,datetime.datetime.strptime(data[key][:19], "%Y-%m-%dT%H:%M:%S"))
        if isinstance(field_type,String):
            setattr(obj,field,data[key][:field_type.length])
