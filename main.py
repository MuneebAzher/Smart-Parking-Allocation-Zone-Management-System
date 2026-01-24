"""
Main Module - Entry point and demonstration of the Smart Parking System
Provides a command-line interface for interacting with the parking system
"""

import sys
from datetime import datetime
from ParkingSystem import ParkingSystem
from ParkingSlot import SlotType
from Vehicle import VehicleType
from ParkingRequest import RequestPriority


def print_header(text: str) -> None:
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_subheader(text: str) -> None:
    """Print a formatted subheader"""
    print(f"\n--- {text} ---")


def print_table(headers: list, rows: list) -> None:
    """Print a simple table"""
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)))


def initialize_demo_system() -> ParkingSystem:
    """Initialize the parking system with demo data"""
    print_header("Initializing Smart Parking System")
    
    # Create system
    system = ParkingSystem("Downtown Parking Complex")
    
    # Create zones
    print_subheader("Creating Zones")
    zone_a = system.create_zone("ZONE-A", "Zone A - North Wing", "Premium parking near main entrance")
    zone_b = system.create_zone("ZONE-B", "Zone B - South Wing", "Standard parking")
    zone_c = system.create_zone("ZONE-C", "Zone C - East Wing", "Economy parking")
    zone_d = system.create_zone("ZONE-D", "Zone D - West Wing", "Overflow parking")
    
    print(f"  Created: {zone_a}")
    print(f"  Created: {zone_b}")
    print(f"  Created: {zone_c}")
    print(f"  Created: {zone_d}")
    
    # Set up adjacency relationships
    system.add_adjacent_zones("ZONE-A", "ZONE-B")
    system.add_adjacent_zones("ZONE-B", "ZONE-C")
    system.add_adjacent_zones("ZONE-C", "ZONE-D")
    system.add_adjacent_zones("ZONE-D", "ZONE-A")
    print("\n  Zone adjacency relationships established")
    
    # Create areas and slots
    print_subheader("Creating Parking Areas")
    
    # Zone A - Premium
    area_a1 = system.create_area("A1", "A1 - VIP Section", "ZONE-A", floor=1, num_slots=5, slot_type=SlotType.VIP)
    area_a2 = system.create_area("A2", "A2 - Electric Vehicles", "ZONE-A", floor=1, num_slots=8, slot_type=SlotType.ELECTRIC)
    area_a3 = system.create_area("A3", "A3 - Regular", "ZONE-A", floor=1, num_slots=12, slot_type=SlotType.REGULAR)
    
    # Zone B - Standard
    area_b1 = system.create_area("B1", "B1 - Ground Floor", "ZONE-B", floor=1, num_slots=20, slot_type=SlotType.REGULAR)
    area_b2 = system.create_area("B2", "B2 - Compact Cars", "ZONE-B", floor=1, num_slots=15, slot_type=SlotType.COMPACT)
    
    # Zone C - Economy
    area_c1 = system.create_area("C1", "C1 - Large Vehicles", "ZONE-C", floor=1, num_slots=10, slot_type=SlotType.LARGE)
    area_c2 = system.create_area("C2", "C2 - Motorcycles", "ZONE-C", floor=1, num_slots=20, slot_type=SlotType.MOTORCYCLE)
    area_c3 = system.create_area("C3", "C3 - Handicap", "ZONE-C", floor=1, num_slots=8, slot_type=SlotType.HANDICAP)
    
    # Zone D - Overflow
    area_d1 = system.create_area("D1", "D1 - Overflow Regular", "ZONE-D", floor=1, num_slots=30, slot_type=SlotType.REGULAR)
    
    print(f"  Created 9 parking areas with total {sum(z.get_total_slots() for z in system.zones.values())} slots")
    
    # Register demo vehicles
    print_subheader("Registering Demo Vehicles")
    
    vehicles = [
        ("ABC-1234", VehicleType.CAR, "John Smith", "555-0101"),
        ("XYZ-5678", VehicleType.SUV, "Jane Doe", "555-0102"),
        ("EV-9999", VehicleType.ELECTRIC, "Bob Tesla", "555-0103"),
        ("MOTO-001", VehicleType.MOTORCYCLE, "Mike Rider", "555-0104"),
        ("TRUCK-42", VehicleType.TRUCK, "Tom Hauler", "555-0105"),
        ("VIP-7777", VehicleType.CAR, "CEO Executive", "555-0106"),
        ("COMP-123", VehicleType.COMPACT, "Sara Small", "555-0107"),
    ]
    
    for plate, v_type, owner, contact in vehicles:
        v = system.register_vehicle(plate, v_type, owner, contact)
        print(f"  Registered: {v}")
    
    # Set special flags
    system.get_vehicle("V-VIP-7777").set_vip_status(True)
    
    print(f"\n  Total registered vehicles: {len(system.vehicles)}")
    
    return system


def display_system_status(system: ParkingSystem) -> None:
    """Display current system status"""
    print_header("System Status")
    
    stats = system.get_system_statistics()
    
    print(f"\n  System: {stats['system_name']}")
    print(f"  Total Zones: {stats['zones_count']}")
    print(f"  Total Slots: {stats['total_slots']}")
    print(f"  Available: {stats['available_slots']}")
    print(f"  Occupied: {stats['occupied_slots']}")
    print(f"  Utilization: {stats['overall_utilization']:.1f}%")
    
    print_subheader("Zone Details")
    zone_stats = system.get_zone_statistics()
    
    headers = ["Zone", "Name", "Total", "Available", "Occupied", "Util %"]
    rows = [
        [z["zone_id"], z["name"][:20], z["total_slots"], z["available_slots"], 
         z["occupied_slots"], f"{z['utilization']:.1f}%"]
        for z in zone_stats
    ]
    print_table(headers, rows)


def display_requests(system: ParkingSystem) -> None:
    """Display all requests"""
    print_header("Parking Requests")
    
    pending = system.get_pending_requests()
    active = system.get_active_requests()
    
    print_subheader(f"Pending Requests ({len(pending)})")
    if pending:
        headers = ["Request ID", "Vehicle", "Preferred Zone", "Priority", "State"]
        rows = [
            [r.request_id, r.vehicle_id, r.preferred_zone_id or "Any", 
             r.priority.name, r.state.value]
            for r in pending
        ]
        print_table(headers, rows)
    else:
        print("  No pending requests")
    
    print_subheader(f"Active Requests ({len(active)})")
    if active:
        headers = ["Request ID", "Vehicle", "Slot", "Zone", "State"]
        rows = [
            [r.request_id, r.vehicle_id, r.allocated_slot_id or "-", 
             r.allocated_zone_id or "-", r.state.value]
            for r in active
        ]
        print_table(headers, rows)
    else:
        print("  No active requests")


def demo_parking_workflow(system: ParkingSystem) -> None:
    """Demonstrate the parking workflow"""
    print_header("Parking Workflow Demo")
    
    # Create parking requests
    print_subheader("Creating Parking Requests")
    
    # Request 1: Regular car preferring Zone A
    result1 = system.create_parking_request(
        "V-ABC-1234",
        preferred_zone_id="ZONE-A",
        priority=RequestPriority.NORMAL
    )
    print(f"  Request 1: {result1.message}")
    
    # Request 2: VIP car
    result2 = system.create_parking_request(
        "V-VIP-7777",
        preferred_zone_id="ZONE-A",
        priority=RequestPriority.VIP
    )
    print(f"  Request 2: {result2.message}")
    
    # Request 3: Electric vehicle
    result3 = system.create_parking_request(
        "V-EV-9999",
        preferred_zone_id="ZONE-A",
        priority=RequestPriority.NORMAL
    )
    print(f"  Request 3: {result3.message}")
    
    # Request 4: Truck needing large slot
    result4 = system.create_parking_request(
        "V-TRUCK-42",
        preferred_zone_id="ZONE-C",
        priority=RequestPriority.NORMAL
    )
    print(f"  Request 4: {result4.message}")
    
    # Occupy slots
    print_subheader("Vehicles Entering Slots")
    
    for result in [result1, result2, result3, result4]:
        if result.success:
            system.occupy_parking(result.request.request_id)
            print(f"  {result.request.vehicle_id} entered {result.slot_id}")
    
    # Display updated status
    display_system_status(system)
    display_requests(system)
    
    # Release one vehicle
    print_subheader("Vehicle Exiting")
    if result1.success:
        release_info = system.release_parking(result1.request.request_id)
        if release_info:
            duration = release_info["release_info"]["duration"]
            print(f"  {result1.request.vehicle_id} exited after {duration:.0f} seconds")


def demo_rollback(system: ParkingSystem) -> None:
    """Demonstrate rollback functionality"""
    print_header("Rollback Demo")
    
    # Show operation history
    print_subheader("Recent Operation History")
    history = system.get_operation_history(5)
    
    if history:
        headers = ["Operation", "Type", "Entity", "Timestamp"]
        rows = [
            [h["operation_id"][:12], h["operation_type"], 
             f"{h['entity_type']}:{h['entity_id'][:8]}", 
             h["timestamp"][11:19]]
            for h in history
        ]
        print_table(headers, rows)
    
    # Rollback last operation
    if system.can_rollback():
        print_subheader("Rolling Back Last Operation")
        result = system.rollback_last_operation()
        print(f"  Result: {result['message']}")
        print(f"  Operations rolled back: {result['operations_count']}")


def interactive_menu(system: ParkingSystem) -> None:
    """Interactive menu for the parking system"""
    while True:
        print_header("Smart Parking System - Main Menu")
        print("""
  1. View System Status
  2. View All Zones
  3. View Requests
  4. Create Parking Request
  5. Occupy Slot (Vehicle Entry)
  6. Release Slot (Vehicle Exit)
  7. Cancel Request
  8. View Operation History
  9. Rollback Last Operation
  10. Rollback Last K Operations
  0. Exit
        """)
        
        choice = input("Enter your choice: ").strip()
        
        if choice == "0":
            print("\nExiting. Goodbye!")
            break
        elif choice == "1":
            display_system_status(system)
        elif choice == "2":
            print_subheader("All Zones")
            for zone in system.zones.values():
                print(f"\n  {zone}")
                for area in zone.areas.values():
                    print(f"    - {area}")
        elif choice == "3":
            display_requests(system)
        elif choice == "4":
            print_subheader("Create Parking Request")
            print("  Available vehicles:")
            for v in system.vehicles.values():
                if not v.is_parked:
                    print(f"    - {v.vehicle_id} ({v.license_plate})")
            
            vehicle_id = input("  Enter vehicle ID: ").strip()
            zone_id = input("  Preferred zone (or press Enter for any): ").strip() or None
            
            result = system.create_parking_request(vehicle_id, zone_id)
            print(f"\n  Result: {result.message}")
        elif choice == "5":
            active = [r for r in system.get_active_requests() if r.state.value == "allocated"]
            if not active:
                print("  No allocated requests to occupy")
                continue
            print("  Allocated requests:")
            for r in active:
                print(f"    - {r.request_id}: {r.vehicle_id} -> {r.allocated_slot_id}")
            
            request_id = input("  Enter request ID: ").strip()
            if system.occupy_parking(request_id):
                print("  Slot occupied successfully")
            else:
                print("  Failed to occupy slot")
        elif choice == "6":
            active = [r for r in system.get_active_requests() if r.state.value == "occupied"]
            if not active:
                print("  No occupied slots to release")
                continue
            print("  Occupied slots:")
            for r in active:
                print(f"    - {r.request_id}: {r.vehicle_id} at {r.allocated_slot_id}")
            
            request_id = input("  Enter request ID: ").strip()
            result = system.release_parking(request_id)
            if result:
                print(f"  Slot released. Duration: {result['release_info']['duration']:.0f}s")
            else:
                print("  Failed to release slot")
        elif choice == "7":
            pending = system.get_pending_requests()
            allocated = [r for r in system.get_active_requests() if r.state.value == "allocated"]
            
            print("  Cancellable requests:")
            for r in pending + allocated:
                print(f"    - {r.request_id}: {r.vehicle_id} ({r.state.value})")
            
            request_id = input("  Enter request ID: ").strip()
            if system.cancel_parking_request(request_id):
                print("  Request cancelled successfully")
            else:
                print("  Failed to cancel request")
        elif choice == "8":
            print_subheader("Operation History")
            history = system.get_operation_history(10)
            
            if history:
                for h in history:
                    print(f"  [{h['timestamp'][11:19]}] {h['operation_type']}: {h['entity_type']}")
            else:
                print("  No operations recorded")
        elif choice == "9":
            if system.can_rollback():
                result = system.rollback_last_operation()
                print(f"  {result['message']}")
            else:
                print("  No operations to rollback")
        elif choice == "10":
            k = int(input("  Enter number of operations to rollback: "))
            result = system.rollback_last_k_operations(k)
            print(f"  {result['message']}")
        else:
            print("  Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("     SMART PARKING ALLOCATION & ZONE MANAGEMENT SYSTEM")
    print("          DSA Semester Project Implementation")
    print("=" * 60)
    
    # Initialize system with demo data
    system = initialize_demo_system()
    
    # Show initial status
    display_system_status(system)
    
    # Run demo workflow
    demo_parking_workflow(system)
    
    # Demo rollback
    demo_rollback(system)
    
    # Ask if user wants interactive mode
    print_header("Demo Complete")
    choice = input("\nWould you like to enter interactive mode? (y/n): ").strip().lower()
    
    if choice == 'y':
        interactive_menu(system)
    else:
        print("\nFinal System State:")
        print(system.to_json())


if __name__ == "__main__":
    main()
