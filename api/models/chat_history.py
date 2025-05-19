from peewee import Model, CharField, TextField, SqliteDatabase, DateTimeField
from datetime import datetime
import os

# Asegura que el directorio exista
os.makedirs("db", exist_ok=True)
db = SqliteDatabase("db/chats.db")

class BaseModel(Model):
    class Meta:
        database = db

class ChatHistory(BaseModel):
    numero_procedimiento = CharField(null=True)
    nombre_documento = CharField(null=True)
    pregunta = TextField()
    respuesta = TextField()
    timestamp = DateTimeField(default=datetime.now)

db.connect()
db.create_tables([ChatHistory])