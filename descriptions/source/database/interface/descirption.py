from sqlalchemy.orm import declarative_base


RestConsumerBaseInterface = declarative_base()
class RESTDescriptionBase(RestConsumerBaseInterface):
    base_metadata = RestConsumerBaseInterface
    __abstract__ = True