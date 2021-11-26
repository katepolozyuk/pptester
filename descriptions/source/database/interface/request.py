from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String

from typing import Any, List, Dict, Optional

from sqlalchemy.sql.sqltypes import Boolean
from .descirption import RESTDescriptionBase


class RESTRequest(RESTDescriptionBase):
    __tablename__ = "request"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource = relationship("RESTResource", back_populates="requests")
    resource_id = Column(Integer, ForeignKey("resource.id", ondelete="CASCADE"))
    test_status = Column(Integer, default=0)
    method = Column(String(64))
    body = Column(String(2048))
    response_template = Column(String(2048))


class RESTRequestInterface:
    session_maker:sessionmaker

    @classmethod
    def __init__(self, engine:Engine) -> None:
        self.session_maker = sessionmaker(bind=engine)

    @classmethod
    def add_request_record(self, resource_id:int, method:str, body:str, response_template:str) -> Any:
        with self.session_maker() as session:
            with session.begin():
                resource_description = RESTRequest(resource_id=resource_id, method=method, body=body, response_template=response_template)
                session.add(resource_description)

    @classmethod
    def get_request_records(self, resource_id:int) -> List[Any]:
        with self.session_maker() as session:
            with session.begin():
                records = session.query(RESTRequest).filter(RESTRequest.resource_id == resource_id).all()
                convert = RESTRequestInterface.__convert_list_to_dict
                return convert(records)

    @classmethod
    def get_request_record(self, resource_id:int, request_id:int) -> List[Any]:
        with self.session_maker() as session:
            with session.begin():
                record = session.query(RESTRequest).filter(RESTRequest.resource_id == resource_id).filter(RESTRequest.id == request_id).first()
                convert = RESTRequestInterface.__convert_to_dict
                if record is not None:
                    return convert(record)

    @classmethod
    def delete_request_record(self, resource_id:int, request_id:int) -> None:
        with self.session_maker() as session:
            with session.begin():
                record = session.query(RESTRequest).filter(RESTRequest.resource_id == resource_id).filter(RESTRequest.id == request_id)
                record.delete()

    @classmethod
    def update_request_record(self, resource_id:int, request_id:int, method:str, body:str, response_template:str) -> None:
        with self.session_maker() as session:
            with session.begin():
                record = session.query(RESTRequest).filter(RESTRequest.resource_id == resource_id).filter(RESTRequest.id == request_id).first()
                record.method = method
                record.body = body
                record.response_template = response_template

    @classmethod
    def update_request_record_test_status(self, resource_id:int, request_id:int, new_test_status:int) -> None:
        with self.session_maker() as session:
            with session.begin():
                record = session.query(RESTRequest).filter(RESTRequest.resource_id == resource_id).filter(RESTRequest.id == request_id).first()
                record.test_status = int(new_test_status)

    @staticmethod
    def __convert_to_dict(record:Any) -> Dict[Any, Any]:
        return dict(record.__dict__)

    @staticmethod
    def __convert_list_to_dict(records:Any) -> List[Optional[Dict[Any, Any]]]:
        convert_to_dict = RESTRequestInterface.__convert_to_dict
        return [convert_to_dict(record) for record in records if record is not None]
