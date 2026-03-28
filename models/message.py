from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database.db import Base

class MessageDB(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    room_id = Column(String, index=True)