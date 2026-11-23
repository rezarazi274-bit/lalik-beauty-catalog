"""Telegram Mini App initData verification (HMAC-SHA256)."""
import hashlib,hmac,json,time
from urllib.parse import parse_qsl

def validate_init_data(init_data:str, bot_token:str, max_age:int=86400):
    if not init_data or not bot_token: return None
    try:
        pairs=dict(parse_qsl(init_data,keep_blank_values=True)); received=pairs.pop("hash",None)
        if not received: return None
        check="\n".join(f"{k}={v}" for k,v in sorted(pairs.items()))
        secret=hmac.new(b"WebAppData",bot_token.encode(),hashlib.sha256).digest()
        expected=hmac.new(secret,check.encode(),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected,received): return None
        auth_date=int(pairs.get("auth_date",0))
        if auth_date<=0 or time.time()-auth_date>max_age: return None
        return json.loads(pairs["user"]) if "user" in pairs else None
    except (ValueError,TypeError,KeyError,json.JSONDecodeError): return None
