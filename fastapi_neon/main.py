from fastapi import FastAPI, HTTPException
from typing import Union,Optional
from fastapi_neon import settings
from sqlmodel import Field,Session,SQLModel,create_engine,select

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)


Connection_string=str(settings.DATABASE_URL).replace("postgresql","postgresql+psycopg")

#start Engine
engine = create_engine(Connection_string,connect_args= {"sslmode":"require"}, pool_recycle=300)

#create db schema

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


app= FastAPI()

@app.get("/health/")
def health():
    create_db_and_tables()
    return {"status": "ok"}

@app.get("/")
def read_root():
    return{ "Hello": "World"}
# endpoint for data insertion in DB
@app.post("/todos/")
def create_todo(todo:Todo):
    with Session(engine) as session:
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo
# endpoint for data updation in DB
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo_update: Todo):
    with Session(engine) as session:
        # Fetch todo item from database
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo item not found")
        # Update todo item's content if provided
        if todo_update.content:
            todo.content = todo_update.content
        session.commit()
        session.refresh(todo)
        return todo
# endpoint for data  deletion from DB
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    with Session(engine) as session:
        # Fetch todo item from database
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo item not found") 
        session.delete(todo)
        session.commit()
        return {"message": "Todo item deleted successfully"}



# @app.get("/todos/")
# def read_todos():
#     with Session(engine) as session:
#         todos=session.exec(select(Todo)).all()
#         return todos
            

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}