from typing import Optional

from app.models.core import CoreModel, IDModelMixin
from app.models.enum_type import CleaningType


class CleaningBase(CoreModel):
    """
    All common characteristics of our Cleaning resources
    """
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    cleaning_type: Optional[CleaningType] = CleaningType.spot_clean

    class Config:
        use_enum_values = True


class CleaningCreate(CleaningBase):
    name: str
    price: float


class CleaningInDB(IDModelMixin, CleaningBase):
    name: str
    price: float
    cleaning_type: CleaningType


class CleaningPublic(IDModelMixin, CleaningBase):
    pass
