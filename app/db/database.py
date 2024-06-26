from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.config import database_url_aiomysql
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.db.models import Base, TArea, TClient, TRequest
from app.core.data_request import DataRequest
from abc import ABC, abstractmethod


class IDBWorker(ABC):
    async def select_request_filter_client(self, client_name: str) -> list[DataRequest]:
        pass

    async def select_request_filter_area(self, area_name: str) -> list[DataRequest]:
        pass

    async def select_request_filter_area_client(self, area_name: str, client_name: str) -> list[DataRequest]:
        pass

    async def select_request(self) -> list[DataRequest]:
        pass


class DBWorker(IDBWorker):
    def __init__(self):
        self.engine = create_async_engine(database_url_aiomysql(), echo=True)
        self.session = async_sessionmaker(self.engine)

    async def clear_tables(self) -> None:
        '''
        clear_tables all tables
        :return:
        '''
        async with self.session() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    def __convert_answer_to_request(self, answer: list[TRequest]) -> list[DataRequest]:
        '''
        convert SQLAlchemy obj to pydantic model DataRequest
        :param answer:
        :return:
        '''
        return [DataRequest.model_validate(row, from_attributes=True) for row in answer]

    async def select_request_filter_client(self, client_name: str) -> list[DataRequest]:
        '''
        :param client_name: fullname_client for filtering
        :return:
        '''
        async with self.session() as conn:
            query = (
                select(TRequest)
                .select_from(TRequest)
                .join(TClient, TRequest.client_id == TClient.id)
                .filter(TClient.fullname_client == client_name)
            )
            res = await conn.execute(query)
            return self.__convert_answer_to_request(res.scalars().all())

    async def select_request_filter_area(self, area_name: str) -> list[DataRequest]:
        '''
        :param area_name: fullname_area for filtering
        :return:
        '''
        async with self.session() as conn:
            query = (
                select(TRequest)
                .select_from(TRequest)
                .join(TArea, TRequest.area_id == TArea.id)
                .filter(TArea.fullname_area == area_name)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = await conn.execute(query)
            return self.__convert_answer_to_request(res.scalars().all())

    async def select_request_filter_area_client(self, area_name: str, client_name: str) -> list[DataRequest]:
        '''
        :param area_name: fullname_client for filtering
        :param client_name: fullname_area for filtering
        :return:
        '''
        async with self.session() as conn:
            query = (
                select(TRequest)
                .select_from(TRequest)
                .join(TArea, TRequest.area_id == TArea.id)
                .join(TClient, TRequest.client_id == TClient.id)
                .filter(TArea.fullname_area == area_name)
                .filter(TClient.fullname_client == client_name)
            )
            res = await conn.execute(query)
            return self.__convert_answer_to_request(res.scalars().all())

    async def select_request(self) -> list[DataRequest]:
        '''
        :return: select request without a filter
        '''
        async with self.session() as conn:
            query = (
                select(TRequest)
                .select_from(TRequest)
            )
            res = await conn.execute(query)
            return self.__convert_answer_to_request(res.scalars().all())
