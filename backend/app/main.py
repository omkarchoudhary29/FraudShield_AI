from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import List
from datetime import datetime

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routes import auth, transactions, fraud, analytics, reviews, alerts

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="FraudShield AI API",
    description="Real-time fraud detection system with AI-powered analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(fraud.router)
app.include_router(analytics.router)
app.include_router(reviews.router)
app.include_router(alerts.router)

@app.get("/")
async def root():
    return {
        "message": "FraudShield AI API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.websocket("/ws/transactions")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time transaction updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            
            # Echo back or handle specific commands
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/ws/stream-transactions")
async def stream_recent_transactions():
    """Get recent transactions for streaming (alternative to WebSocket)"""
    db = get_database()
    
    # Get last 10 transactions
    cursor = db.transactions.find().sort("timestamp", -1).limit(10)
    transactions = await cursor.to_list(length=10)
    
    for txn in transactions:
        txn["_id"] = str(txn["_id"])
    
    return transactions

# Background task to broadcast new transactions
async def broadcast_new_transactions():
    """Background task to monitor and broadcast new transactions"""
    db = get_database()
    last_check = datetime.utcnow()
    
    while True:
        await asyncio.sleep(2)  # Check every 2 seconds
        
        # Find new transactions since last check
        new_transactions = await db.transactions.find({
            "timestamp": {"$gt": last_check}
        }).to_list(length=10)
        
        if new_transactions:
            for txn in new_transactions:
                txn["_id"] = str(txn["_id"])
                await manager.broadcast({
                    "type": "new_transaction",
                    "data": txn
                })
            
            last_check = datetime.utcnow()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
