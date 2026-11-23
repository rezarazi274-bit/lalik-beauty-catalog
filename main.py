import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from security import validate_init_data
from schemas import ProductOut, OrderIn, PaymentRequest, PaymentVerify
from payments import gateway
from database import Product, Order

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    from pathlib import Path
    seed=Path(__file__).parent / "data" / "initial_db.sql"
    if seed.exists():
        with engine.begin() as conn:
            for statement in seed.read_text(encoding="utf-8").split(";"):
                if statement.strip(): conn.exec_driver_sql(statement)
    yield
app=FastAPI(title="Lalik Beauty API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS","*").split(","), allow_methods=["*"], allow_headers=["*"])

def telegram_user(x_telegram_init_data: str=Header(default="")):
    if os.getenv("ENVIRONMENT","development") == "development" and not x_telegram_init_data:
        return {"id": 0, "first_name":"مهمان"}
    user=validate_init_data(x_telegram_init_data, os.getenv("BOT_TOKEN",""))
    if not user: raise HTTPException(401,"داده تلگرام نامعتبر است")
    return user

@app.get("/api/health")
def health(): return {"status":"ok"}
@app.get("/api/products", response_model=list[ProductOut])
def products(db:Session=Depends(get_db)):
    return db.query(Product).filter(Product.is_active==True).all()
@app.get("/api/products/{product_id}", response_model=ProductOut)
def product(product_id:int, db:Session=Depends(get_db)):
    item=db.query(Product).filter_by(id=product_id,is_active=True).first()
    if not item: raise HTTPException(404,"محصول پیدا نشد")
    return item
@app.post("/api/orders")
def create_order(data:OrderIn, user=Depends(telegram_user), db:Session=Depends(get_db)):
    total=0
    for line in data.items:
        prod=db.query(Product).filter_by(id=line.product_id,is_active=True).first()
        if not prod: raise HTTPException(400,"محصول نامعتبر است")
        total += prod.price_toman*line.quantity
    if total <= 0: raise HTTPException(400,"سبد خرید خالی است")
    order=Order(telegram_user_id=int(user.get("id",0)), total_toman=total, status="pending", address=data.address)
    db.add(order); db.commit(); db.refresh(order)
    return {"order_id":order.id,"total_toman":total,"status":order.status}
@app.post("/api/payments/request")
def payment_request(data:PaymentRequest, user=Depends(telegram_user), db:Session=Depends(get_db)):
    order=db.query(Order).filter_by(id=data.order_id,telegram_user_id=int(user.get("id",0))).first()
    if not order: raise HTTPException(404,"سفارش پیدا نشد")
    return gateway.request(order.id,order.total_toman,data.callback_url)
@app.post("/api/payments/verify")
def payment_verify(data:PaymentVerify, user=Depends(telegram_user), db:Session=Depends(get_db)):
    order=db.query(Order).filter_by(id=data.order_id,telegram_user_id=int(user.get("id",0))).first()
    if not order: raise HTTPException(404,"سفارش پیدا نشد")
    result=gateway.verify(data.authority,order.total_toman)
    if result["success"]: order.status="paid"; db.commit()
    return result
