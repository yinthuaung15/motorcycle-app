from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
import os

@dataclass
class Motorcycle:
    id: int
    brand: str
    model: str
    year: int
    bike_type: str
    engine: str
    color: str
    price: int
    stock: int
    description: str
    features: List[str]
    installment_down: int
    installment_monthly: int
    installment_period: int
    warranty: str
    image_url: str = ""
    status: str = "in_stock"
    created_at: str = ""
    updated_at: str = ""
    
    def to_dict(self):
        return self.__dict__

@dataclass
class Order:
    id: int
    user_id: int
    user_name: str
    username: str
    bike_id: int
    brand: str
    model: str
    price: int
    quantity: int
    total: int
    payment_method: str
    customer_name: str
    phone: str
    address: str
    status: str = "pending"
    created_at: str = ""
    
    def to_dict(self):
        return self.__dict__

class JSONDatabase:
    def __init__(self, filename):
        self.filename = f"data/{filename}"
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        os.makedirs('data', exist_ok=True)
    
    def load(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save(self, data):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

class MotorcycleDB(JSONDatabase):
    def __init__(self):
        super().__init__('motorcycles.json')
    
    def get_all(self):
        return self.load()
    
    def get_by_id(self, bike_id):
        bikes = self.load()
        for bike in bikes:
            if bike['id'] == bike_id:
                return bike
        return None
    
    def add(self, bike_data):
        bikes = self.load()
        bike_data['id'] = max([b['id'] for b in bikes], default=0) + 1
        bike_data['created_at'] = datetime.now().isoformat()
        bike_data['updated_at'] = datetime.now().isoformat()
        bikes.append(bike_data)
        self.save(bikes)
        return bike_data
    
    def update(self, bike_id, updates):
        bikes = self.load()
        for bike in bikes:
            if bike['id'] == bike_id:
                bike.update(updates)
                bike['updated_at'] = datetime.now().isoformat()
                self.save(bikes)
                return bike
        return None
    
    def delete(self, bike_id):
        bikes = self.load()
        bikes = [b for b in bikes if b['id'] != bike_id]
        self.save(bikes)
    
    def update_stock(self, bike_id, quantity, operation='add'):
        bikes = self.load()
        for bike in bikes:
            if bike['id'] == bike_id:
                if operation == 'add':
                    bike['stock'] += quantity
                elif operation == 'remove':
                    bike['stock'] = max(0, bike['stock'] - quantity)
                elif operation == 'set':
                    bike['stock'] = quantity
                
                bike['status'] = 'in_stock' if bike['stock'] > 0 else 'out_of_stock'
                bike['updated_at'] = datetime.now().isoformat()
                self.save(bikes)
                return bike['stock']
        return None
    
    def get_available(self):
        return [b for b in self.load() if b['stock'] > 0]
    
    def search(self, query):
        query = query.lower()
        return [b for b in self.load() if query in b['brand'].lower() or 
                query in b['model'].lower() or query in b['bike_type'].lower()]

class OrderDB(JSONDatabase):
    def __init__(self):
        super().__init__('orders.json')
    
    def get_all(self):
        return self.load()
    
    def add(self, order_data):
        orders = self.load()
        order_data['id'] = len(orders) + 1
        order_data['created_at'] = datetime.now().isoformat()
        orders.append(order_data)
        self.save(orders)
        return order_data
    
    def update_status(self, order_id, status):
        orders = self.load()
        for order in orders:
            if order['id'] == order_id:
                order['status'] = status
                self.save(orders)
                return order
        return None

# Initialize databases
motorcycle_db = MotorcycleDB()
order_db = OrderDB()

# Seed default motorcycles if empty
def seed_motorcycles():
    if not motorcycle_db.get_all():
        default_bikes = [
            {
                "brand": "Honda", "model": "Wave 125i", "year": 2024,
                "bike_type": "ဆိုင်ကယ်", "engine": "125cc",
                "color": "အနက်၊ အဖြူ၊ အနီ",
                "price": 2850000, "stock": 5,
                "description": "Honda Wave 125i ဆိုင်ကယ်။ ဆီစားသက်သာ၊ မောင်းရတာအဆင်ပြေ။",
                "features": ["ဆီစားနှုန်း 65km/L", "125cc 4-Stroke", "Disc/Drum ဘရိတ်"],
                "installment_down": 500000, "installment_monthly": 85000,
                "installment_period": 24, "warranty": "၂ နှစ်"
            },
            {
                "brand": "Yamaha", "model": "FZ 150i", "year": 2024,
                "bike_type": "ဆိုင်ကယ်", "engine": "150cc",
                "color": "အနက်၊ အပြာ",
                "price": 4950000, "stock": 3,
                "description": "Yamaha FZ 150i Sporty ဆိုင်ကယ်။ လူငယ်ကြိုက်။",
                "features": ["150cc FI", "Disc/Disc ဘရိတ်", "LED Headlight"],
                "installment_down": 800000, "installment_monthly": 150000,
                "installment_period": 24, "warranty": "၂ နှစ်"
            },
            {
                "brand": "Suzuki", "model": "V-Strom 250SX", "year": 2024,
                "bike_type": "Adventure", "engine": "250cc",
                "color": "အနက်၊ အဝါ",
                "price": 8950000, "stock": 2,
                "description": "Suzuki V-Strom 250SX Adventure ဆိုင်ကယ်။ ခရီးဝေးအတွက်အကောင်းဆုံး။",
                "features": ["250cc Twin Cylinder", "ABS ဘရိတ်", "12L ဆီတိုင်ကီ"],
                "installment_down": 1500000, "installment_monthly": 280000,
                "installment_period": 24, "warranty": "၃ နှစ်"
            },
            {
                "brand": "Honda", "model": "ADV 160", "year": 2024,
                "bike_type": "Adventure Scooter", "engine": "160cc",
                "color": "အနက်၊ အနီ",
                "price": 6200000, "stock": 4,
                "description": "Honda ADV 160 စကူတာ။ မြို့တွင်းရော ခရီးဝေးပါအဆင်ပြေ။",
                "features": ["160cc FI", "ABS ဘရိတ်", "Smart Key"],
                "installment_down": 1000000, "installment_monthly": 200000,
                "installment_period": 24, "warranty": "၂ နှစ်"
            },
            {
                "brand": "CFMoto", "model": "450SR", "year": 2024,
                "bike_type": "Sport", "engine": "450cc",
                "color": "အနက်၊ အနီ၊ အပြာ",
                "price": 12500000, "stock": 1,
                "description": "CFMoto 450SR Sport Bike။ အားပြင်းအင်ဂျင်၊ ခေတ်မီဒီဇိုင်း။",
                "features": ["450cc Parallel Twin", "ABS Dual Channel", "TFT Display"],
                "installment_down": 2500000, "installment_monthly": 350000,
                "installment_period": 24, "warranty": "၃ နှစ်"
            },
        ]
        for bike in default_bikes:
            motorcycle_db.add(bike)
        print("✅ Default motorcycles seeded!")

seed_motorcycles()