"""
Driver Assignment Service
Handles driver search, assignment, and tracking
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)

# Mock driver database
DRIVERS = {
    "drv_001": {
        "id": "drv_001",
        "name": "Rahul Kumar",
        "phone": "+919123456789",
        "vehicle": "Bike",
        "rating": 4.8,
        "status": "available",
        "location": {"lat": 28.7041, "lng": 77.1025}
    },
    "drv_002": {
        "id": "drv_002",
        "name": "Amit Singh",
        "phone": "+919123456790",
        "vehicle": "Bike",
        "rating": 4.6,
        "status": "available",
        "location": {"lat": 28.7041, "lng": 77.1025}
    },
    "drv_003": {
        "id": "drv_003",
        "name": "Priya Sharma",
        "phone": "+919123456791",
        "vehicle": "Scooter",
        "rating": 4.9,
        "status": "busy",
        "location": {"lat": 28.7041, "lng": 77.1025}
    }
}


class DriverService:
    """Handles driver operations"""
    
    def __init__(self):
        self.active_deliveries = {}
    
    def find_available_drivers(self, location: Dict[str, float], radius_km: int = 5) -> List[Dict[str, Any]]:
        """
        Find available drivers near location
        
        Args:
            location: Customer location coordinates
            radius_km: Search radius in kilometers
        
        Returns:
            List of available drivers
        """
        available = [d for d in DRIVERS.values() if d["status"] == "available"]
        logger.info(f"Found {len(available)} available drivers")
        return available
    
    def assign_driver(self, order_id: str, driver_id: str, restaurant_location: Dict, customer_location: Dict) -> Dict[str, Any]:
        """
        Assign driver to order
        
        Args:
            order_id: Order identifier
            driver_id: Driver identifier
            restaurant_location: Restaurant coordinates
            customer_location: Customer delivery address
        
        Returns:
            Assignment result with ETA
        """
        driver = DRIVERS.get(driver_id)
        
        if not driver:
            return {"success": False, "error": "Driver not found"}
        
        if driver["status"] != "available":
            return {"success": False, "error": "Driver not available"}
        
        # Update driver status
        DRIVERS[driver_id]["status"] = "on_delivery"
        
        # Calculate ETA (mock calculation)
        pickup_eta = random.randint(5, 10)
        delivery_eta = pickup_eta + random.randint(15, 25)
        
        # Store delivery info
        self.active_deliveries[order_id] = {
            "driver_id": driver_id,
            "driver_name": driver["name"],
            "driver_phone": driver["phone"],
            "driver_rating": driver["rating"],
            "vehicle": driver["vehicle"],
            "pickup_eta": pickup_eta,
            "delivery_eta": delivery_eta,
            "status": "assigned",
            "assigned_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Driver {driver['name']} assigned to order {order_id}")
        logger.info(f"   Pickup ETA: {pickup_eta} mins, Delivery ETA: {delivery_eta} mins")
        
        return {
            "success": True,
            "driver": driver,
            "pickup_eta_minutes": pickup_eta,
            "delivery_eta_minutes": delivery_eta,
            "total_eta_minutes": delivery_eta
        }
    
    def update_driver_location(self, driver_id: str, location: Dict[str, float]) -> bool:
        """Update driver's current location"""
        if driver_id in DRIVERS:
            DRIVERS[driver_id]["location"] = location
            return True
        return False
    
    def mark_picked_up(self, order_id: str) -> bool:
        """Mark order as picked up from restaurant"""
        if order_id in self.active_deliveries:
            self.active_deliveries[order_id]["status"] = "picked_up"
            logger.info(f"✅ Order {order_id} picked up by driver")
            return True
        return False
    
    def mark_delivered(self, order_id: str) -> bool:
        """Mark order as delivered"""
        if order_id in self.active_deliveries:
            delivery = self.active_deliveries[order_id]
            delivery["status"] = "delivered"
            delivery["delivered_at"] = datetime.now().isoformat()
            
            # Free up driver
            driver_id = delivery["driver_id"]
            if driver_id in DRIVERS:
                DRIVERS[driver_id]["status"] = "available"
            
            logger.info(f"✅ Order {order_id} delivered successfully")
            return True
        return False
    
    def get_delivery_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get current delivery status"""
        return self.active_deliveries.get(order_id)
