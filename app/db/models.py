"""
Database Models
SQLAlchemy ORM models for all entities
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey,
    Text, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from app.db.database import Base


# Enums
class OrderStatus(str, enum.Enum):
    CART = "cart"
    PLACED = "placed"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class DriverStatus(str, enum.Enum):
    OFFLINE = "offline"
    AVAILABLE = "available"
    BUSY = "busy"
    ON_DELIVERY = "on_delivery"


class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class AgentType(str, enum.Enum):
    CUSTOMER_ORDER = "customer_order"
    RESTAURANT_COORDINATION = "restaurant_coordination"
    DRIVER_ASSIGNMENT = "driver_assignment"
    DELIVERY_TRACKING = "delivery_tracking"
    CUSTOMER_SUPPORT = "customer_support"
    POST_DELIVERY = "post_delivery"


# Models
class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    addresses = Column(JSONB, default=list)  # List of address objects
    payment_methods = Column(JSONB, default=list)  # List of payment method IDs
    preferences = Column(JSONB, default=dict)  # Dietary preferences, favorites
    total_orders = Column(Integer, default=0)
    lifetime_value = Column(Float, default=0.0)
    dnd_registered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    orders = relationship("Order", back_populates="customer")
    call_sessions = relationship("CallSession", back_populates="customer")
    
    __table_args__ = (
        Index('idx_customer_phone', 'phone_number'),
        Index('idx_customer_email', 'email'),
    )


class Restaurant(Base):
    """Restaurant model"""
    __tablename__ = "restaurants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    email = Column(String(255))
    address = Column(JSONB, nullable=False)
    location = Column(JSONB, nullable=False)  # {lat, lng}
    cuisine_types = Column(JSONB, default=list)
    operating_hours = Column(JSONB, nullable=False)
    average_prep_time = Column(Integer, default=30)  # minutes
    rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    menu_items = relationship("MenuItem", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")


class MenuItem(Base):
    """Menu Item model"""
    __tablename__ = "menu_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    is_available = Column(Boolean, default=True)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    spice_level = Column(Integer, default=0)  # 0-5
    allergens = Column(JSONB, default=list)
    customization_options = Column(JSONB, default=list)
    tags = Column(JSONB, default=list)  # For semantic search
    embedding = Column(JSONB, nullable=True)  # Vector embedding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    
    __table_args__ = (
        Index('idx_menu_restaurant', 'restaurant_id'),
        Index('idx_menu_category', 'category'),
    )


class Order(Base):
    """Order model"""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=True)
    
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    items = Column(JSONB, nullable=False)  # List of {item_id, quantity, customizations, price}
    
    delivery_address = Column(JSONB, nullable=False)
    delivery_instructions = Column(Text)
    
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.CART, nullable=False, index=True)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method_id = Column(String(255))
    payment_intent_id = Column(String(255))
    
    estimated_prep_time = Column(Integer)  # minutes
    estimated_delivery_time = Column(DateTime)
    actual_delivery_time = Column(DateTime)
    
    placed_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    ready_at = Column(DateTime, nullable=True)
    picked_up_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    rating = Column(Integer, nullable=True)  # 1-5
    feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    driver = relationship("Driver", back_populates="orders")
    
    __table_args__ = (
        Index('idx_order_customer', 'customer_id'),
        Index('idx_order_status', 'status'),
        Index('idx_order_number', 'order_number'),
    )


class Driver(Base):
    """Driver model"""
    __tablename__ = "drivers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    status = Column(SQLEnum(DriverStatus), default=DriverStatus.OFFLINE, nullable=False)
    current_location = Column(JSONB)  # {lat, lng, accuracy, timestamp}
    vehicle_type = Column(String(50))
    vehicle_number = Column(String(50))
    
    rating = Column(Float, default=0.0)
    total_deliveries = Column(Integer, default=0)
    total_ratings = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    orders = relationship("Order", back_populates="driver")
    
    __table_args__ = (
        Index('idx_driver_status', 'status'),
        Index('idx_driver_phone', 'phone_number'),
    )


class CallSession(Base):
    """Call Session model"""
    __tablename__ = "call_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_sid = Column(String(255), unique=True, nullable=False, index=True)
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    
    direction = Column(SQLEnum(CallDirection), nullable=False)
    from_number = Column(String(20), nullable=False)
    to_number = Column(String(20), nullable=False)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    
    initial_agent = Column(SQLEnum(AgentType), nullable=False)
    transcript = Column(Text)
    recording_url = Column(String(500))
    
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(50), nullable=True)
    
    summary = Column(Text)
    outcome = Column(String(100))  # order_placed, issue_resolved, etc.
    
    cost_stt = Column(Float, default=0.0)
    cost_tts = Column(Float, default=0.0)
    cost_llm = Column(Float, default=0.0)
    cost_twilio = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    metadata = Column(JSONB, default=dict)
    
    # Relationships
    customer = relationship("Customer", back_populates="call_sessions")
    agent_transitions = relationship("AgentTransition", back_populates="call_session")
    
    __table_args__ = (
        Index('idx_call_sid', 'call_sid'),
        Index('idx_call_customer', 'customer_id'),
    )


class AgentTransition(Base):
    """Agent Transition tracking"""
    __tablename__ = "agent_transitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_session_id = Column(UUID(as_uuid=True), ForeignKey("call_sessions.id"), nullable=False)
    
    from_agent = Column(SQLEnum(AgentType), nullable=True)
    to_agent = Column(SQLEnum(AgentType), nullable=False)
    
    reason = Column(String(255))
    context_summary = Column(Text)
    
    transitioned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call_session = relationship("CallSession", back_populates="agent_transitions")
    
    __table_args__ = (
        Index('idx_transition_call', 'call_session_id'),
    )


class FAQ(Base):
    """FAQ for support agent"""
    __tablename__ = "faqs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100))
    tags = Column(JSONB, default=list)
    embedding = Column(JSONB, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
