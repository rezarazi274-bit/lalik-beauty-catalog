"""Mock gateway implementing request/redirect/verify lifecycle. Replace with provider SDK for live payments."""
import secrets
class MockGateway:
    def __init__(self): self.pending={}
    def request(self,order_id:int,amount_toman:int,callback_url:str):
        authority="LALIK-"+secrets.token_hex(8).upper(); self.pending[authority]=(order_id,amount_toman)
        return {"success":True,"provider":"mock-zarinpal-idpay","authority":authority,"payment_url":f"{callback_url}?Authority={authority}&Status=OK","message":"درگاه آزمایشی؛ پرداخت واقعی انجام نمی‌شود."}
    def verify(self,authority:str,amount_toman:int):
        record=self.pending.pop(authority,None)
        if not record or record[1]!=amount_toman: return {"success":False,"message":"پرداخت نامعتبر یا قبلاً بررسی شده است."}
        return {"success":True,"ref_id":"MOCK-"+authority[-8:],"message":"پرداخت آزمایشی با موفقیت تأیید شد."}
gateway=MockGateway()
