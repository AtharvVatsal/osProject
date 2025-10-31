"""
Advanced Traffic Signal Controller System
Demonstrates: Concurrency, Synchronization, Thread Priority, Deadlock Prevention
"""

import threading
import time
import queue
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import random
from datetime import datetime


class SignalState(Enum):
    """Traffic signal states"""
    RED = "🔴 RED"
    YELLOW = "🟡 YELLOW"
    GREEN = "🟢 GREEN"
    EMERGENCY = "🚨 EMERGENCY"


class VehicleType(Enum):
    """Types of vehicles in the system"""
    NORMAL = "🚗"
    EMERGENCY = "🚑"
    PEDESTRIAN = "🚶"


@dataclass
class TrafficStats:
    """Statistics for traffic monitoring"""
    total_cycles: int = 0
    total_wait_time: float = 0.0
    emergency_responses: int = 0
    deadlock_preventions: int = 0
    average_green_time: float = 0.0
    vehicles_passed: int = 0


class EmergencyVehicle:
    """Represents an emergency vehicle requiring priority"""
    def __init__(self, direction: str, vehicle_id: int):
        self.direction = direction
        self.vehicle_id = vehicle_id
        self.timestamp = time.time()
        self.handled = False


class Intersection:
    """
    Shared resource representing the intersection
    Implements synchronization and deadlock prevention
    """
    def __init__(self, intersection_id: str):
        self.intersection_id = intersection_id
        self.lock = threading.RLock()  # Reentrant lock for nested locking
        self.active_directions: List[str] = []
        
        # Semaphore: Max 2 opposing directions can be green
        self.green_semaphore = threading.Semaphore(2)
        
        # Condition variables for coordination
        self.state_changed = threading.Condition(self.lock)
        
        # Emergency vehicle queue (thread-safe)
        self.emergency_queue: queue.PriorityQueue = queue.PriorityQueue()
        
        # Deadlock prevention: ordering of directions
        self.direction_priority = {"NORTH": 0, "EAST": 1, "SOUTH": 2, "WEST": 3}
        
        # Traffic density tracking for adaptive timing
        self.traffic_density: Dict[str, int] = {
            "NORTH": 0, "SOUTH": 0, "EAST": 0, "WEST": 0
        }
        
        # Statistics
        self.stats = TrafficStats()
        
        # Pedestrian crossing state
        self.pedestrian_waiting: Dict[str, bool] = {
            "NORTH": False, "SOUTH": False, "EAST": False, "WEST": False
        }
        
        # Event log for monitoring
        self.event_log: queue.Queue = queue.Queue(maxsize=100)
        
    def log_event(self, event: str):
        """Thread-safe event logging"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.event_log.put_nowait(f"[{timestamp}] {event}")
        except queue.Full:
            # Remove oldest event if full
            try:
                self.event_log.get_nowait()
                self.event_log.put_nowait(f"[{timestamp}] {event}")
            except:
                pass
    
    def get_opposing_direction(self, direction: str) -> str:
        """Get the opposing direction"""
        opposites = {
            "NORTH": "SOUTH", "SOUTH": "NORTH",
            "EAST": "WEST", "WEST": "EAST"
        }
        return opposites.get(direction, "")
    
    def get_conflicting_directions(self, direction: str) -> List[str]:
        """Get all directions that conflict with the given direction"""
        conflicts = {
            "NORTH": ["EAST", "WEST"],
            "SOUTH": ["EAST", "WEST"],
            "EAST": ["NORTH", "SOUTH"],
            "WEST": ["NORTH", "SOUTH"]
        }
        return conflicts.get(direction, [])
    
    def has_emergency_vehicle(self) -> Optional[EmergencyVehicle]:
        """Check if there's an emergency vehicle waiting"""
        try:
            # Peek at queue without removing
            priority, emergency = self.emergency_queue.get_nowait()
            self.emergency_queue.put((priority, emergency))
            return emergency if not emergency.handled else None
        except queue.Empty:
            return None
    
    def add_emergency_vehicle(self, direction: str):
        """Add emergency vehicle with highest priority"""
        vehicle_id = self.stats.emergency_responses + 1
        emergency = EmergencyVehicle(direction, vehicle_id)
        # Priority: negative timestamp for FIFO with highest priority
        self.emergency_queue.put((-time.time(), emergency))
        self.log_event(f"🚨 EMERGENCY vehicle {vehicle_id} approaching from {direction}")
        
        with self.state_changed:
            self.state_changed.notify_all()
    
    def can_proceed(self, direction: str, check_emergency: bool = True) -> bool:
        """
        Thread-safe check if direction can safely turn green
        Implements deadlock prevention through ordered resource acquisition
        """
        with self.lock:
            # Check for emergency vehicles first
            if check_emergency:
                emergency = self.has_emergency_vehicle()
                if emergency and emergency.direction != direction:
                    return False  # Wait for emergency to pass
            
            # Check if conflicting directions are active
            conflicts = self.get_conflicting_directions(direction)
            for conflict in conflicts:
                if conflict in self.active_directions:
                    self.stats.deadlock_preventions += 1
                    return False
            
            # Check opposite direction (can both be green)
            opposite = self.get_opposing_direction(direction)
            if opposite in self.active_directions:
                # Both opposing directions can be green together
                return True
            
            # If no active directions, allow
            if len(self.active_directions) == 0:
                return True
            
            # Check if we can add another direction (max 2)
            if len(self.active_directions) < 2:
                return True
            
            return False
    
    def enter_intersection(self, direction: str, is_emergency: bool = False):
        """Thread-safe method to mark direction as active"""
        self.green_semaphore.acquire()
        
        with self.lock:
            self.active_directions.append(direction)
            state = "EMERGENCY" if is_emergency else "GREEN"
            self.log_event(f"✓ {direction} is now {state}")
            self.stats.total_cycles += 1
            
            if is_emergency:
                self.stats.emergency_responses += 1
    
    def exit_intersection(self, direction: str):
        """Thread-safe method to mark direction as inactive"""
        with self.lock:
            if direction in self.active_directions:
                self.active_directions.remove(direction)
                self.log_event(f"✗ {direction} is now RED")
                
        self.green_semaphore.release()
        
        with self.state_changed:
            self.state_changed.notify_all()
    
    def update_traffic_density(self, direction: str, density: int):
        """Update traffic density for adaptive timing"""
        with self.lock:
            self.traffic_density[direction] = max(0, min(100, density))
    
    def get_adaptive_green_time(self, direction: str, base_time: float) -> float:
        """Calculate adaptive green time based on traffic density"""
        with self.lock:
            density = self.traffic_density[direction]
            # Scale from 50% to 150% of base time based on density
            multiplier = 0.5 + (density / 100.0)
            return base_time * multiplier
    
    def set_pedestrian_waiting(self, direction: str, waiting: bool):
        """Set pedestrian waiting status"""
        with self.lock:
            self.pedestrian_waiting[direction] = waiting
            if waiting:
                self.log_event(f"🚶 Pedestrian waiting at {direction}")


class TrafficSignal(threading.Thread):
    """
    Individual traffic signal thread
    Implements thread lifecycle, state management, and coordination
    """
    def __init__(self, direction: str, intersection: Intersection, 
                 base_green_time: float = 5.0, yellow_time: float = 2.0):
        super().__init__(daemon=True)
        self.direction = direction
        self.intersection = intersection
        self.state = SignalState.RED
        self.base_green_time = base_green_time
        self.yellow_time = yellow_time
        self.running = True
        self.cycle_count = 0
        self.last_state_change = time.time()
        
    def wait_for_turn(self, timeout: float = 30.0) -> bool:
        """Wait for safe access to intersection with timeout"""
        start_wait = time.time()
        
        while self.running:
            if self.intersection.can_proceed(self.direction):
                wait_time = time.time() - start_wait
                self.intersection.stats.total_wait_time += wait_time
                return True
            
            # Check for timeout to prevent starvation
            if time.time() - start_wait > timeout:
                self.intersection.log_event(
                    f"⚠ {self.direction} timeout - forcing access"
                )
                return True
            
            time.sleep(0.1)  # Small sleep to prevent busy waiting
        
        return False
    
    def handle_emergency(self) -> bool:
        """Check and handle emergency vehicle in this direction"""
        emergency = self.intersection.has_emergency_vehicle()
        
        if emergency and emergency.direction == self.direction and not emergency.handled:
            # Emergency vehicle in our direction
            self.state = SignalState.EMERGENCY
            self.intersection.enter_intersection(self.direction, is_emergency=True)
            
            # Clear emergency vehicle quickly (3 seconds)
            time.sleep(3.0)
            
            emergency.handled = True
            self.intersection.exit_intersection(self.direction)
            
            return True
        
        return False
    
    def run(self):
        """Main thread execution loop"""
        # Initial random offset to prevent all signals starting together
        time.sleep(random.uniform(0, 2))
        
        while self.running:
            try:
                # Check for emergency vehicles
                if self.handle_emergency():
                    continue
                
                # Wait for safe access
                if not self.wait_for_turn():
                    break
                
                # Calculate adaptive green time
                green_time = self.intersection.get_adaptive_green_time(
                    self.direction, self.base_green_time
                )
                
                # GREEN PHASE
                self.state = SignalState.GREEN
                self.last_state_change = time.time()
                self.intersection.enter_intersection(self.direction)
                
                # Simulate vehicles passing
                vehicles_passed = random.randint(3, 8)
                self.intersection.stats.vehicles_passed += vehicles_passed
                
                time.sleep(green_time)
                
                # YELLOW PHASE
                self.state = SignalState.YELLOW
                self.last_state_change = time.time()
                self.intersection.log_event(f"⚠ {self.direction} is now YELLOW")
                
                time.sleep(self.yellow_time)
                
                # RED PHASE
                self.state = SignalState.RED
                self.last_state_change = time.time()
                self.intersection.exit_intersection(self.direction)
                
                self.cycle_count += 1
                
                # Minimum red time before trying again
                time.sleep(2.0)
                
            except Exception as e:
                self.intersection.log_event(f"❌ Error in {self.direction}: {str(e)}")
                break
    
    def stop(self):
        """Gracefully stop the thread"""
        self.running = False
    
    def get_state_info(self) -> Dict:
        """Get current state information"""
        return {
            "direction": self.direction,
            "state": self.state.value,
            "cycle_count": self.cycle_count,
            "time_in_state": time.time() - self.last_state_change
        }


class TrafficController:
    """
    Main controller managing multiple intersections
    Coordinates signal timing and handles system-wide events
    """
    def __init__(self, num_intersections: int = 1):
        self.intersections: List[Intersection] = []
        self.signals: List[TrafficSignal] = []
        self.running = False
        
        # Create intersections and signals
        for i in range(num_intersections):
            intersection = Intersection(f"Intersection-{i+1}")
            self.intersections.append(intersection)
            
            # Create signals for each direction
            for direction in ["NORTH", "SOUTH", "EAST", "WEST"]:
                signal = TrafficSignal(direction, intersection)
                self.signals.append(signal)
    
    def start(self):
        """Start all traffic signals"""
        if self.running:
            return
        
        self.running = True
        for signal in self.signals:
            signal.start()
        
        # Log system start
        for intersection in self.intersections:
            intersection.log_event("🚦 Traffic Control System STARTED")
    
    def stop(self):
        """Stop all traffic signals gracefully"""
        if not self.running:
            return
        
        self.running = False
        
        # Log system stop
        for intersection in self.intersections:
            intersection.log_event("🛑 Traffic Control System STOPPING")
        
        # Stop all signals
        for signal in self.signals:
            signal.stop()
        
        # Wait for threads to finish (with timeout)
        for signal in self.signals:
            signal.join(timeout=2.0)
    
    def get_system_stats(self) -> Dict:
        """Get aggregated system statistics"""
        total_stats = TrafficStats()
        
        for intersection in self.intersections:
            stats = intersection.stats
            total_stats.total_cycles += stats.total_cycles
            total_stats.total_wait_time += stats.total_wait_time
            total_stats.emergency_responses += stats.emergency_responses
            total_stats.deadlock_preventions += stats.deadlock_preventions
            total_stats.vehicles_passed += stats.vehicles_passed
        
        # Calculate averages
        if total_stats.total_cycles > 0:
            total_stats.average_green_time = total_stats.total_wait_time / total_stats.total_cycles
        
        return {
            "total_cycles": total_stats.total_cycles,
            "average_wait_time": f"{total_stats.average_green_time:.2f}s",
            "emergency_responses": total_stats.emergency_responses,
            "deadlock_preventions": total_stats.deadlock_preventions,
            "vehicles_passed": total_stats.vehicles_passed
        }
    
    def trigger_emergency(self, intersection_idx: int = 0, direction: str = "NORTH"):
        """Trigger an emergency vehicle event"""
        if 0 <= intersection_idx < len(self.intersections):
            self.intersections[intersection_idx].add_emergency_vehicle(direction)
    
    def update_traffic_density(self, intersection_idx: int, direction: str, density: int):
        """Update traffic density for adaptive timing"""
        if 0 <= intersection_idx < len(self.intersections):
            self.intersections[intersection_idx].update_traffic_density(direction, density)


if __name__ == "__main__":
    # Simple test
    controller = TrafficController(num_intersections=1)
    controller.start()
    
    print("Traffic Control System Running...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping system...")
        controller.stop()
        print("System stopped.")