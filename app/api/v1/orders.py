"""
Orders API
Endpoints for order management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.db.database import get_db
from app.db.models import Order, Customer, OrderStatus

router = APIRouter()


@router.get("/")
async def list_orders(
    customer_id: str = None,
    status: OrderStatus = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List orders with filters"""
    query = select(Order)
    
    if customer_id:
        query = query.where(Order.customer_id == uuid.UUID(customer_id))
    
    if status:
        query = query.where(Order.status == status)
    
    query = query.limit(limit).order_by(Order.created_at.desc())
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return {"orders": [order for order in orders]}


@router.get("/{order_id}")
async def get_order(order_id: str, db: AsyncSession = Depends(get_db)):
    """Get order by ID"""
    result = await db.execute(
        select(Order).where(Order.id == uuid.UUID(order_id))
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"order": order}


@router.post("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: OrderStatus,
    db: AsyncSession = Depends(get_db)
):
    """Update order status"""
    result = await db.execute(
        select(Order).where(Order.id == uuid.UUID(order_id))
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.status = status
    await db.commit()
    
    return {"order_id": order_id, "status": status}
