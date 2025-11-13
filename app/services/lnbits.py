import httpx
import uuid
from app.config import LNBITS_URL, LNBITS_ADMIN_KEY

async def create_user_wallet(user_name: str):
    async with httpx.AsyncClient() as client:
        try:
            wallet_name = f"satmap_{user_name}_{uuid.uuid4().hex[:8]}"
            response = await client.post(
                f"{LNBITS_URL}/api/v1/wallet",
                json={"name": wallet_name},
                headers={"X-Api-Key": LNBITS_ADMIN_KEY}
            )
            data = response.json()
            if response.status_code == 200 or response.status_code == 201:
                return {
                    "id": data.get("id"),
                    "wallets": [{
                        "id": data.get("id"),
                        "adminkey": data.get("admin_key", data.get("adminkey")),
                        "inkey": data.get("inkey")
                    }]
                }
            return {"error": f"Failed to create wallet: {data}"}
        except Exception as e:
            return {"error": str(e)}

async def get_wallet_balance(wallet_key: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{LNBITS_URL}/api/v1/wallet",
                headers={"X-Api-Key": wallet_key}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

async def create_invoice(wallet_key: str, amount_sats: int, memo: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{LNBITS_URL}/api/v1/payments",
                json={"out": False, "amount": amount_sats, "memo": memo},
                headers={"X-Api-Key": wallet_key}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

async def pay_invoice(wallet_adminkey: str, payment_request: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{LNBITS_URL}/api/v1/payments",
                json={"out": True, "bolt11": payment_request},
                headers={"X-Api-Key": wallet_adminkey}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

async def send_sats_to_wallet(to_wallet_invoice_key: str, amount_sats: int, memo: str):
    async with httpx.AsyncClient() as client:
        try:
            invoice_response = await client.post(
                f"{LNBITS_URL}/api/v1/payments",
                json={"out": False, "amount": amount_sats, "memo": memo},
                headers={"X-Api-Key": to_wallet_invoice_key}
            )
            invoice_data = invoice_response.json()
            
            if "error" in invoice_data or "payment_request" not in invoice_data:
                return {"error": "Failed to create invoice"}
            
            payment_response = await client.post(
                f"{LNBITS_URL}/api/v1/payments",
                json={"out": True, "bolt11": invoice_data["payment_request"]},
                headers={"X-Api-Key": LNBITS_ADMIN_KEY}
            )
            return payment_response.json()
        except Exception as e:
            return {"error": str(e)}

async def check_invoice(payment_hash: str, wallet_key: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{LNBITS_URL}/api/v1/payments/{payment_hash}",
                headers={"X-Api-Key": wallet_key}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

