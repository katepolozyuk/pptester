from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String

from typing import Any, List, Dict, Optional
from .descirption import RESTDescriptionBase


class RESTResource(RESTDescriptionBase):
    __tablename__ = "resource"

    id = Column(Integer, primary_key=True, autoincrement=True)
    requests = relationship("RESTRequest", back_populates="resource")
    service = relationship("RESTService", back_populates="resources")
    service_id = Column(Integer, ForeignKey("service.id", ondelete="CASCADE"))
    endpoint = Column(String(1024))


class RESTResourceInterface:
    session_maker:sessionmaker

    @classmethod
    def __init__(self, engine:Engine) -> None:
        self.session_maker = sessionmaker(bind=engine)

    @classmethod
    def add_resource_record(self, service_id:int, resource_endpoint:str) -> Any:
        with self.session_maker() as session:
            with session.begin():
                resource_description = RESTResource(service_id=service_id, endpoint=resource_endpoint)
                session.add(resource_description)

    @classmethod
    def update_resource_record(self, service_id:int, resource_id:int, resource_endpoint:str) -> None:
        with self.session_maker() as session:
            with session.begin():
                record = session.query(RESTResource).filter(RESTResource.service_id == service_id).filter(RESTResource.id == resource_id).first()
                record.endpoint = resource_endpoint

    @classmethod
    def get_resource_records(self, service_id:int) -> Optional[List[Dict[Any, Any]]]:
        with self.session_maker() as session:
            with session.begin():
                records = session.query(RESTResource).filter(RESTResource.service_id == service_id).all()
                convert = RESTResourceInterface.__convert_list_to_dict
                return convert(records)

    @classmethod
    def get_resource_record(self, service_id:int, resource_id:int) -> Optional[Any]:
        with self.session_maker() as session:
            with session.begin():
                record = session.query(RESTResource).filter(RESTResource.service_id == service_id).filter(RESTResource.id == resource_id).first()
                convert = RESTResourceInterface.__convert_to_dict
                if record is not None:
                    return convert(record)

    @classmethod
    def delete_resource_record(self, service_id:int, resource_id:int) -> None:
        with self.session_maker() as session:
            with session.begin():
                record = session.query(RESTResource).filter(RESTResource.service_id == service_id).filter(RESTResource.id == resource_id)
                record.delete()

    @staticmethod
    def __convert_to_dict(record:Any) -> Dict[Any, Any]:
        return dict(record.__dict__)

    @staticmethod
    def __convert_list_to_dict(records:Any) -> List[Optional[Dict[Any, Any]]]:
        convert_to_dict = RESTResourceInterface.__convert_to_dict
        return [convert_to_dict(record) for record in records if record is not None]
