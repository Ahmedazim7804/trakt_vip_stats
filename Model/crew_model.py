from sqlmodel import SQLModel, Field

class Crew(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    image: str