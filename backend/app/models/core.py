from pydantic import BaseModel


class CoreModel(BaseModel):
    """
    Any common logic to be shared by all models go here
    """
    pass


class IDModelMixin(BaseModel):
    id: int
