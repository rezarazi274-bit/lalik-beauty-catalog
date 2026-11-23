import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
DB_URL=os.getenv("DATABASE_URL","sqlite:///./lalik.db")
engine=create_engine(DB_URL, connect_args={"check_same_thread":False} if DB_URL.startswith("sqlite") else {})
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()
class Product(Base):
    __tablename__="products"
    id=Column(Integer,primary_key=True,index=True); name=Column(String(120),nullable=False); description=Column(Text,default=""); price_toman=Column(Integer,nullable=False); category=Column(String(80),default="آرایشی"); image_url=Column(String(500),default=""); is_active=Column(Boolean,default=True)
class Order(Base):
    __tablename__="orders"
    id=Column(Integer,primary_key=True,index=True); telegram_user_id=Column(Integer,index=True); total_toman=Column(Integer,nullable=False); status=Column(String(30),default="pending"); address=Column(Text,default="")
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
