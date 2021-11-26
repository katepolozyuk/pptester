from utils.environment import find_environment_variable

from database import routes
from database.interface import service
from database.interface import resource
from database.interface import request
from database.interface import descirption
from sqlalchemy import create_engine


class PPTesterInterface:
    service_dao:service.RESTServiceInterface
    resource_dao:resource.RESTResourceInterface
    request_dao:request.RESTRequestInterface

    @classmethod
    def __init__(self, working_directory:str, remote_db:bool) -> None:
        self.__init__metadata(working_directory, remote_db)
        self.service_dao = service.RESTServiceInterface(self.service_db_engine)
        self.resource_dao = resource.RESTResourceInterface(self.service_db_engine)
        self.request_dao = request.RESTRequestInterface(self.service_db_engine)

    @classmethod
    def __init__metadata(self, working_directory:str, remote_db:bool) -> None:
        if not remote_db:
            self.service_db_endpoint = routes.build_sqlite_local_endpoint(working_directory, db_folder="data", db_name="services", db_suffix="db")
        else:
            database_name = find_environment_variable("MARIADB_DATABASE_NAME", "service_descriptions_db")
            database_username = find_environment_variable("MARIADB_DATABASE_USERNAME", "firefly")
            database_password = find_environment_variable("MARIADB_DATABASE_PASSWORD", "firefly_developer_1234")
            database_host_address = find_environment_variable("MARIADB_DATABASE_HOST_ADDRESS", "descriptions_database")
            database_host_port = int(find_environment_variable("MARIADB_DATABASE_HOST_PORT", "3306"))

            routes.wait_for_mariadb(database_host_address, database_host_port, database_name, database_username, database_password)
            self.service_db_endpoint = routes.build_mariadb_endpoint(database_host_address, database_host_port, database_name, database_username, database_password)

        self.service_db_engine = create_engine(self.service_db_endpoint, echo=True)
        self.service_base_metadata = descirption.RESTDescriptionBase.base_metadata
        self.service_base_metadata.metadata.create_all(self.service_db_engine)