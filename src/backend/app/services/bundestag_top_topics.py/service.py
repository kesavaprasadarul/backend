from datetime import datetime
from typing import Optional
from backend.app.crud.CRUDDIPBundestag.crud_drucksache import CRUDDIPDrucksache


from backend.app.models.deutscher_bundestag.drucksache_model import DIPDrucksache


class DIPDrucksacheService:
    def __init__(self, crud: CRUDDIPDrucksache):
        self.crud = crud

    def get_model(self):
        return DIPDrucksache

    def get(self, id: int) -> Optional[DIPDrucksache]:
        result = self.crud.read(id)
        if result:
            return DIPDrucksache

    def _build_filter_options(
        self,
        planned_flight_date: Range | None = None,
        flight_date: Range | None = None,
        created_at: Range | None = None,
    ) -> list:
        filters = []
        if planned_flight_date:
            if planned_flight_date.min:
                filters.append(FlightModel.planned_flight_date >= planned_flight_date.min)
            if planned_flight_date.max:
                filters.append(FlightModel.planned_flight_date <= planned_flight_date.max)
        if flight_date:
            if planned_flight_date.min:
                filters.append(FlightModel.flight_date >= flight_date.min)
            if planned_flight_date.max:
                filters.append(FlightModel.flight_date <= flight_date.max)
        if created_at:
            if created_at.min:
                filters.append(FlightModel.created_at >= created_at.min)
            if created_at.max:
                filters.append(FlightModel.created_at <= created_at.max)
        return filters

    def query_count(
        self,
        planned_flight_date: Range | None = None,
        flight_date: Range | None = None,
        created_at: Range | None = None,
    ) -> int:
        filters = self._build_filter_options(
            planned_flight_date=planned_flight_date,
            flight_date=flight_date,
            created_at=created_at,
        )

        return self.postgres_service.query().filter(*filters).count()

    def query(
        self,
        limit: int,
        skip: 0,
        planned_flight_date: Range | None = None,
        flight_date: Range | None = None,
        created_at: Range | None = None,
    ) -> list[Flight]:
        filters = self._build_filter_options(
            planned_flight_date=planned_flight_date,
            flight_date=flight_date,
            created_at=created_at,
        )

        results = self.postgres_service.query().filter(*filters).limit(limit).offset(skip).all()
        return [Flight.from_orm(r) for r in results]

    def add(self, msg: Flight) -> Flight:
        now = datetime.now()
        msg.created_at = now
        msg.updated_at = now
        inserted_obj = self.postgres_service.add(FlightModel(**msg.dict()))
        return self.get(inserted_obj.id)

    def update(self, msg: Flight) -> Flight:
        msg.updated_at = datetime.now()
        data = msg.dict(exclude_unset=True)

        del data["id"]
        del data["created_at"]

        self.postgres_service.update(msg.id, data)
        return self.get(msg.id)

    def delete(self, id: int) -> None:
        self.postgres_service.delete(id)
