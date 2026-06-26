from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.statistics import StatisticsResponse
from app.services.dashboard import StatisticsService

router = APIRouter()


@router.get("", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)) -> StatisticsResponse:
    return StatisticsService(db).get_statistics()
