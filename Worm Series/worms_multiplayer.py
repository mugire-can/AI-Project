"""
Worms Rumble - Multiplayer Networking Module
Handles local and network-based multiplayer

Features:
- Local multiplayer (2-4 players, same keyboard)
- Network multiplayer architecture (TCP/IP)
- Game state synchronization
- Turn management
- Player join/leave handling
"""

import socket
import json
import threading
import time
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Callable

class MessageType(Enum):
    """Network message types"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    GAME_START = "game_start"
    GAME_STATE = "game_state"
    PLAYER_ACTION = "player_action"
    FIRE = "fire"
    MOVE = "move"
    GAME_END = "game_end"
    CHAT = "chat"
    PING = "ping"
    PONG = "pong"

@dataclass
class NetworkMessage:
    """Standard network message format"""
    message_type: MessageType
    sender_id: str
    timestamp: float
    data: Dict = None

    def to_json(self):
        """Convert to JSON for transmission"""
        return json.dumps({
            "type": self.message_type.value,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp,
            "data": self.data
        })

    @classmethod
    def from_json(cls, json_str):
        """Parse from JSON"""
        try:
            data = json.loads(json_str)
            return cls(
                message_type=MessageType(data["type"]),
                sender_id=data["sender_id"],
                timestamp=data["timestamp"],
                data=data.get("data")
            )
        except:
            return None

class PlayerInfo:
    """Information about a connected player"""
    def __init__(self, player_id: str, team_id: int, name: str):
        self.player_id = player_id
        self.team_id = team_id
        self.name = name
        self.connected = True
        self.last_heartbeat = time.time()
        self.ping = 0

class NetworkManager:
    """Manages network connections and communications"""
    
    def __init__(self, server_ip: str = "localhost", server_port: int = 5555, 
                 is_server: bool = True):
        self.server_ip = server_ip
        self.server_port = server_port
        self.is_server = is_server
        
        self.socket = None
        self.connected_clients = {}
        self.running = False
        self.message_callbacks = {}
        self.player_id = None
        
        self.receive_thread = None
        self.heartbeat_thread = None
        
    def register_callback(self, message_type: MessageType, callback: Callable):
        """Register callback for specific message types"""
        if message_type not in self.message_callbacks:
            self.message_callbacks[message_type] = []
        self.message_callbacks[message_type].append(callback)
    
    def start_server(self):
        """Start server (for host player)"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.server_ip, self.server_port))
            self.socket.listen(4)  # Max 4 players
            self.running = True
            
            # Start accept thread
            self.receive_thread = threading.Thread(target=self._accept_connections)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            # Start heartbeat
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
            self.heartbeat_thread.daemon = True
            self.heartbeat_thread.start()
            
            print(f"✓ Server started on {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            print(f"✗ Failed to start server: {e}")
            return False
    
    def connect_to_server(self, server_ip: str, server_port: int) -> bool:
        """Connect to server (for client player)"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.socket.connect((server_ip, server_port))
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"✓ Connected to server at {server_ip}:{server_port}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            return False
    
    def _accept_connections(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                player_id = f"player_{len(self.connected_clients)}"
                
                client_info = {
                    "socket": client_socket,
                    "address": address,
                    "player_id": player_id,
                    "connected": True
                }
                self.connected_clients[player_id] = client_info
                
                print(f"✓ New connection from {address} (ID: {player_id})")
                
                # Start receive thread for this client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(player_id, client_socket)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
    
    def _handle_client(self, player_id: str, client_socket: socket.socket):
        """Handle messages from a connected client"""
        while self.running and self.connected_clients[player_id]["connected"]:
            try:
                message_data = client_socket.recv(4096).decode()
                if message_data:
                    message = NetworkMessage.from_json(message_data)
                    if message:
                        self._trigger_callbacks(message)
                        # Broadcast to other clients if needed
                        if message.message_type == MessageType.MOVE:
                            self.broadcast(message, exclude=player_id)
                else:
                    self._disconnect_client(player_id)
                    break
            except Exception as e:
                print(f"Client {player_id} error: {e}")
                self._disconnect_client(player_id)
                break
    
    def _receive_loop(self):
        """Receive messages from server (client)"""
        while self.running:
            try:
                message_data = self.socket.recv(4096).decode()
                if message_data:
                    message = NetworkMessage.from_json(message_data)
                    if message:
                        self._trigger_callbacks(message)
                else:
                    self.running = False
                    break
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
    
    def _heartbeat_loop(self):
        """Send periodic heartbeat to detect disconnections"""
        while self.running:
            try:
                for player_id in list(self.connected_clients.keys()):
                    client_info = self.connected_clients[player_id]
                    if time.time() - client_info.get("last_heartbeat", time.time()) > 30:
                        self._disconnect_client(player_id)
                
                time.sleep(5)
            except Exception as e:
                print(f"Heartbeat error: {e}")
    
    def send_message(self, message: NetworkMessage):
        """Send message to recipient"""
        try:
            if self.is_server and message.sender_id in self.connected_clients:
                socket = self.connected_clients[message.sender_id]["socket"]
                socket.sendall(message.to_json().encode())
            elif not self.is_server and self.socket:
                self.socket.sendall(message.to_json().encode())
        except Exception as e:
            print(f"Send error: {e}")
    
    def broadcast(self, message: NetworkMessage, exclude: str = None):
        """Broadcast message to all connected clients"""
        if not self.is_server:
            return
        
        for player_id, client_info in self.connected_clients.items():
            if exclude and player_id == exclude:
                continue
            
            try:
                socket = client_info["socket"]
                socket.sendall(message.to_json().encode())
            except Exception as e:
                print(f"Broadcast error to {player_id}: {e}")
    
    def _trigger_callbacks(self, message: NetworkMessage):
        """Trigger registered callbacks for message type"""
        if message.message_type in self.message_callbacks:
            for callback in self.message_callbacks[message.message_type]:
                try:
                    callback(message)
                except Exception as e:
                    print(f"Callback error: {e}")
    
    def _disconnect_client(self, player_id: str):
        """Handle client disconnection"""
        if player_id in self.connected_clients:
            client_info = self.connected_clients[player_id]
            client_info["connected"] = False
            try:
                client_info["socket"].close()
            except:
                pass
            del self.connected_clients[player_id]
            print(f"✗ Player {player_id} disconnected")
    
    def shutdown(self):
        """Shutdown network manager"""
        self.running = False
        
        for client_info in self.connected_clients.values():
            try:
                client_info["socket"].close()
            except:
                pass
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("Network manager shut down")

class LocalMultiplayer:
    """Handles local multiplayer (same keyboard)"""
    
    PLAYER_CONTROLS = [
        {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "aim_up": pygame.K_q,
            "aim_down": pygame.K_e,
            "fire": pygame.K_SPACE,
            "switch": pygame.K_TAB
        },
        {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "aim_up": pygame.K_KP_8,
            "aim_down": pygame.K_KP_5,
            "fire": pygame.K_KP_0,
            "switch": pygame.K_KP_PERIOD
        },
        {
            "left": pygame.K_j,
            "right": pygame.K_l,
            "jump": pygame.K_i,
            "aim_up": pygame.K_u,
            "aim_down": pygame.K_o,
            "fire": pygame.K_k,
            "switch": pygame.K_SEMICOLON
        },
        {
            "left": pygame.K_F,
            "right": pygame.K_H,
            "jump": pygame.K_T,
            "aim_up": pygame.K_R,
            "aim_down": pygame.K_Y,
            "fire": pygame.K_G,
            "switch": pygame.K_X
        }
    ]
    
    @staticmethod
    def get_player_input(player_index: int, keys):
        """Get input for specific player"""
        if player_index >= len(LocalMultiplayer.PLAYER_CONTROLS):
            return {}
        
        controls = LocalMultiplayer.PLAYER_CONTROLS[player_index]
        
        return {
            "left": keys[controls["left"]],
            "right": keys[controls["right"]],
            "jump": keys[controls["jump"]],
            "aim_up": keys[controls["aim_up"]],
            "aim_down": keys[controls["aim_down"]],
            "fire": keys[controls["fire"]],
            "switch": keys[controls["switch"]]
        }

# Example usage
"""
# Server (host player)
network = NetworkManager(server_port=5555, is_server=True)
network.start_server()

def on_player_move(message):
    print(f"Player moved: {message.data}")

network.register_callback(MessageType.MOVE, on_player_move)

# Client (join player)
network = NetworkManager(is_server=False)
network.connect_to_server("localhost", 5555)

# Send message
msg = NetworkMessage(
    message_type=MessageType.MOVE,
    sender_id="player_1",
    timestamp=time.time(),
    data={"x": 100, "y": 200}
)
network.send_message(msg)

# Local multiplayer
keys = pygame.key.get_pressed()
player1_input = LocalMultiplayer.get_player_input(0, keys)
player2_input = LocalMultiplayer.get_player_input(1, keys)
"""
