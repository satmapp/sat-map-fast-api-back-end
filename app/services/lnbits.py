import httpx
from app.config import LNBITS_URL, LNBITS_ADMIN_KEY

async def create_invoice(amount_sats: int, memo: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{LNBITS_URL}/api/v1/payments",
                json={"out": False, "amount": amount_sats, "memo": memo},
                headers={"X-Api-Key": LNBITS_ADMIN_KEY}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

async def pay_invoice(payment_request: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{LNBITS_URL}/api/v1/payments",
                json={"out": True, "bolt11": payment_request},
                headers={"X-Api-Key": LNBITS_ADMIN_KEY}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

async def check_invoice(payment_hash: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{LNBITS_URL}/api/v1/payments/{payment_hash}",
                headers={"X-Api-Key": LNBITS_ADMIN_KEY}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

