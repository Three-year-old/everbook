from sql_app import models
from sql_app.database import engine

models.Base.metadata.create_all(bind=engine)