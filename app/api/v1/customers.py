"""
Customers API
Endpoints for customer management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.db.database import get_db
from app.db.models import Customer

router = APIRouter()


@router.get("/{phone_number}")
async def get_customer_by_phone(
    phone_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get customer by phone number"""
    result = await db.execute(
        select(Customer).where(Customer.phone_number == phone_number)
    )
    customer = result.scalars().first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {"customer": customer}


@router.get("/id/{customer_id}")
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    """Get customer by ID"""
    result = await db.execute(
        select(Customer).where(Customer.id == uuid.UUID(customer_id))
    )
    customer = result.scalars().first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {"customer": customer}
