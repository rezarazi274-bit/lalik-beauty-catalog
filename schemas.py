from pydantic import BaseModel, Field, HttpUrl
class ProductOut(BaseModel):
    id:int; name:str; description:str=""; price_toman:int; category:str="آرایشی"; image_url:str=""
    class Config: from_attributes=True
class OrderLine(BaseModel): product_id:int; quantity:int=Field(ge=1,le=50)
class OrderIn(BaseModel): items:list[OrderLine]; address:str=Field(min_length=5,max_length=1000)
class PaymentRequest(BaseModel): order_id:int; callback_url:str=Field(default="http://localhost:8000/payment-result")
class PaymentVerify(BaseModel): order_id:int; authority:str
