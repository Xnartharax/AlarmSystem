from sqlalchemy import create_engine, Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
db_engine = create_engine("sqlite:///../data/coredata.db")
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind = db_engine)
session = Session()
from datetime import datetime, timedelta
import time
class Alarm(Base):
    __tablename__ = "alarms"
    id = Column(Integer, primary_key=True)
    timer_escalation = Column(DateTime)
    timer_confirmation = Column(DateTime)
    status = Column(Integer)
    confirmed = Column(Boolean)
    updated = Column(Integer)
    
    def escalate(self):
        self.status += 1
        session.commit()

    def update(self, json):
        self.timer_escalation = datetime.strptime(json["timer_escalation"], "%m/%d/%Y, %H:%M")
        self.timer_confirmation = datetime.strptime(json["timer_confirmation"], "%m/%d/%Y, %H:%M")
        self.status = json["status"]
        self.confirmed = json["confirmed"]
        self.updated = json["updated"]
        session.commit()

    def altered(self):
        self.updated = time.time()
        session.commit()

    def postpone(self, hours):
        delta = timedelta(hours=hours)
        self.timer_escalation += delta
        self.timer_confirmation += delta
        self.updated = time.time()
        session.commit()

    def to_dict(self):
        return {
                    "updated": self.updated,
                    "id": self.id,
                    "status": self.status,
                    "timer_escalation": self.timer_escalation.strftime("%m/%d/%Y, %H:%M"),
                    "timer_confirmation": self.timer_confirmation.strftime("%m/%d/%Y, %H:%M"),
                    "confirmed": self.confirmed
                }
                
    def status_check(self):
        now = datetime.now()
        if not self.confirmed:
            if self.timer_confirmation < now:
                self.status = 1
                if self.timer_escalation < now:
                    self.status = 2
                    if self.timer_escalation + timedelta(minutes=1) < now:
                        self.status = 3
                        if self.timer_escalation + timedelta(minutes=2) < now:
                            self.status = 4
            else:
                self.status = 0
    
    def get_escalation_level(self):
        if self.status < 2:
            return 0
        else:
            return self.status-1
    
    def timer(self):
        delta = self.timer_escalation - datetime.now()
        hours = int(delta.seconds / 3600 + delta.days*24)
        minutes = int((delta.seconds % 3600) / 60)
        return f"{hours}:{minutes}"
    
    def format(self):
        return self.timer_escalation.strftime("%d.%m \n %H:%M")

    @staticmethod
    def from_dict(alarm_dict):
        return Alarm(id=alarm_dict["id"], timer_escalation=datetime.strptime(alarm_dict["timer_escalation"], "%m/%d/%Y, %H:%M"),
                        timer_confirmation=datetime.strptime(alarm_dict["timer_confirmation"], "%m/%d/%Y, %H:%M"), confirmed=alarm_dict["confirmed"],
                        updated=alarm_dict["updated"])
        
Base.metadata.create_all(db_engine)