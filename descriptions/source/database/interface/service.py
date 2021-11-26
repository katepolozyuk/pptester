from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime

from typing import Any, List, Dict
from .descirption import RESTDescriptionBase


class RESTService(RESTDescriptionBase):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256))
    url = Column(String(1024), unique=True)
    description = Column(String(4096))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    resources = relationship("RESTResource", back_populates='service', cascade="all, delete, delete-orphan")


class RESTServiceInterface:
    session_maker:sessionmaker

    @classmethod
    def __init__(self, engine:Engine) -> None:
        self.session_maker = sessionmaker(bind=engine)

    @classmethod
    def add_service_record(self, name:str, description:str, url:str) -> None:
        with self.session_maker() as session:
            with session.begin():
                session.add(RESTService(name=name, url=url, description=description))

    @classmethod
    def get_service_record(self, id:int) -> Any:
        with self.session_maker() as session:
            with session.begin():
                convert = RESTServiceInterface.__convert_to_dict
                record = session.query(RESTService).filter(RESTService.id == id).first()
                if record is not None:
                    return convert(record)

    @classmethod
    def get_service_records(self) -> List[Any]:
        with self.session_maker() as session:
            with session.begin():
                records = session.query(RESTService).all()
                convert = RESTServiceInterface.__convert_to_dict
                return [convert(record) for record in records if record is not None]

    @classmethod
    def update_service_record(self, id:int, name:str, description:str, url:str) -> None:
        with self.session_maker() as session:
            with session.begin():
                record = session.query(RESTService).filter(RESTService.id == id).first()
                record.name = name
                record.url = url
                record.description = description

    @classmethod
    def delete_service_record(self, id:int) -> None:
        with self.session_maker() as session:
            with session.begin():
                record = session.query(RESTService).filter(RESTService.id == id).delete()

    @staticmethod
    def __convert_to_dict(record:Any) -> Dict[Any, Any]:
        return dict(record.__dict__)