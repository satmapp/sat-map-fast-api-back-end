# SatMap FastAPI Backend

Backend API for SatMap - Bitcoin commerce mapping with Lightning Network rewards.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql://user:password@host/satmap
LNBITS_URL=https://legend.lnbits.com
LNBITS_ADMIN_KEY=your_admin_key
LNBITS_INVOICE_KEY=your_invoice_key
```

## Initialize Database

```bash
python init_db.py
```

## Run

```bash
uvicorn app.main:app --reload
```

## Access

- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

### Users
- `POST /api/users` - Create user
- `GET /api/users/{user_id}` - Get user
- `GET /api/users/{user_id}/balance` - Get balance

### Commerces
- `POST /api/commerces` - Add commerce
- `GET /api/commerces` - List commerces
- `GET /api/commerces/pending` - Pending verification
- `POST /api/commerces/{id}/verify` - Verify commerce

### Rewards
- `POST /api/rewards/withdraw` - Withdraw sats
