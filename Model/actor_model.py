from sqlmodel import SQLModel, Field

class Actor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    gender: str
    image: str