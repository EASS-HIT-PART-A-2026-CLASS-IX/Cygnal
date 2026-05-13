from sqlmodel import SQLModel, create_engine, Session

# השם של קובץ מסד הנתונים שייווצר לנו בפרויקט
sqlite_file_name = "cygnal.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# הגדרה שמאפשרת ל-FastAPI לעבוד עם SQLite בצורה חלקה במקביל
connect_args = {"check_same_thread": False}

# ה-Engine הוא המנוע שמנהל את התקשורת מול הקובץ
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    """
    פונקציה זו קוראת את כל המודלים שלנו (שיורשים מ-SQLModel)
    ומייצרת עבורם טבלאות ריקות בקובץ הנתונים אם הן לא קיימות.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Dependency עבור FastAPI.
    פותח Session (חיבור) למסד הנתונים עבור כל בקשה, וסוגר אותו בסיומה.
    """
    with Session(engine) as session:
        yield session
