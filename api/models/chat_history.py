from peewee import Model, CharField, TextField, SqliteDatabase, DateTimeField
from datetime import datetime
import os

# Asegura que el directorio exista
os.makedirs("db", exist_ok=True)
db_path = "db/chats.db"
print(f"Conectando a la base de datos en: {os.path.abspath(db_path)}")
db = SqliteDatabase(db_path)
def asegurarse_columna_tipo_documento():
    cursor = db.execute_sql("PRAGMA table_info(chathistory);")
    columnas = [fila[1] for fila in cursor.fetchall()]
    if "tipo_documento" not in columnas:
        print("Agregando columna 'tipo_documento' a la tabla ChatHistory...")
        db.execute_sql("ALTER TABLE chathistory ADD COLUMN tipo_documento TEXT;")
        print("Columna agregada exitosamente.")
    else:
        print("La columna 'tipo_documento' ya existe.")

class BaseModel(Model):
    class Meta:
        database = db
        

class ChatHistory(BaseModel):
    numero_procedimiento = CharField(null=True)
    nombre_documento = CharField(null=True)
    tipo_documento = CharField(null=True)
    pregunta = TextField()
    respuesta = TextField()
    timestamp = DateTimeField(default=datetime.now)

try:
    db.connect()
    print("Conexión exitosa a la base de datos")
    db.create_tables([ChatHistory])
    asegurarse_columna_tipo_documento()
    print("Tablas creadas exitosamente")
except Exception as e:
    print(f"Error al conectar/crear la base de datos: {str(e)}")
    
# Verifica si la columna 'tipo_documento' ya existe


