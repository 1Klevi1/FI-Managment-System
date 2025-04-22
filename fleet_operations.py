# File path for fleet data
FLEET_FILE_PATH = 'db.txt'


# Function to read fleet data from notes.txt
def read_fleet_data():
    fleet_data = []
    try:
        with open(FLEET_FILE_PATH, 'r') as file:
            for line in file:
                if line.strip():  # Ignore empty lines
                    vehicle = line.strip().split(", ")
                    fleet_data.append(vehicle)
    except FileNotFoundError:
        print("Fleet data file not found, starting with an empty fleet.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return fleet_data


# Function to write fleet data to notes.txt
def write_fleet_data(fleet_data):
    try:
        with open(FLEET_FILE_PATH, 'w') as file:
            for vehicle in fleet_data:
                file.write(", ".join(vehicle) + "\n")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


# Function to delete a vehicle from the fleet and db.txt using the vehicle ID
def delete_vehicle(vehicle_id):
    fleet_data = read_fleet_data()

    # Find and remove the vehicle with the given ID
    fleet_data = [vehicle for vehicle in fleet_data if vehicle[0] != vehicle_id]

    # Write the updated fleet data back to the file
    write_fleet_data(fleet_data)
    print(f"Vehicle with ID {vehicle_id} deleted.")


# Function to update a vehicle's data in db.txt using the vehicle ID
def update_vehicle(vehicle_id, new_data):
    fleet_data = read_fleet_data()

    # Find and update the vehicle with the given ID
    for vehicle in fleet_data:
        if vehicle[0] == vehicle_id:
            vehicle[1:] = [new_data['Make'], new_data['Model'], new_data['Year'], new_data['LicensePlate'],
                           new_data['Status']]
            break
    else:
        print(f"Vehicle with ID {vehicle_id} not found.")
        return

    # Write the updated fleet data back to the file
    write_fleet_data(fleet_data)
    print(f"Vehicle with ID {vehicle_id} updated.")


# Function to add a new vehicle to the fleet and notes.txt
def add_vehicle(vehicle):
    fleet_data = read_fleet_data()

    # Auto-increment the ID by adding 1 to the current maximum ID
    vehicle_id = str(len(fleet_data) + 1)
    fleet_data.append([vehicle_id] + vehicle)

    # Write the updated fleet data back to the file
    write_fleet_data(fleet_data)
    print(f"Vehicle with ID {vehicle_id} added.")

def refresh_treeview(management_window):
    """Refresh the treeview to reflect the latest fleet data."""
    # Clear the existing data in the Treeview
    for item in management_window.treeview_management.get_children():
        management_window.treeview_management.delete(item)

    # Insert updated fleet data into the Treeview
    fleet_data = read_fleet_data()
    for vehicle in fleet_data:
        management_window.treeview_management.insert("", "end", values=vehicle)