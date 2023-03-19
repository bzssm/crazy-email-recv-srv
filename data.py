import datetime
from typing import Any

import mysql.connector
import json
from sqlalchemy import Column, String, Text, create_engine, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Message(Base):
    __tablename__ = "t_email_msg"

    id = Column(Integer, primary_key=True, autoincrement=True)
    frm = Column(String(500), index=True)
    to0 = Column(String(500), index=True)
    tos = Column(Text())
    subject = Column(Text())
    content = Column(Text())
    create_time = Column(DateTime())


class DateTimeMarshaller(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        else:
            return json.JSONEncoder.default(self, o)


class DataAccess:
    def __init__(self, host, port, user, password, database):
        self.engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}', pool_recycle=3600, pool_pre_ping=True)
        self.DBSession = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def store_msg(self, msg):
        session = self.DBSession()
        new_msg = Message(
            frm=msg['from'],
            to0=msg['to'][0],
            tos=json.dumps(msg['to']),
            subject=msg['subject'],
            content=msg['content'],
            create_time=datetime.datetime.now()
        )
        session.add(new_msg)
        session.commit()
        session.close()

    def read_from(self, frm):
        session = self.DBSession()
        messages = session.query(Message).filter_by(frm=frm).order_by(Message.create_time.desc()).limit(100).all()
        session.close()
        return self.transform(messages)

    def read_to(self, to):
        session = self.DBSession()
        messages = session.query(Message).filter_by(to0=to).order_by(Message.create_time.desc()).limit(100).all()
        session.close()
        return self.transform(messages)

    def read_all(self):
        session = self.DBSession()
        messages = session.query(Message).order_by(Message.create_time.desc()).limit(100).all()
        session.close()
        return self.transform(messages)

    def transform(self, all):
        rs = []
        for item in all:
            p = {
                "from": item.frm,
                "to0": item.to0,
                "to": json.loads(item.tos),
                "subject": item.subject,
                "content": item.content,
                "time": item.create_time,
            }
            rs.append(p)
        return rs


json_str = open("config.json").read()
cf = json.loads(json_str)["database"]
dataInstance = DataAccess(cf["host"], cf["port"], cf["user"], cf["password"], cf["database"])
