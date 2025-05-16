from opcua import Client
import time

# OPC UA Configuration
OPC_URL = "opc.tcp://192.168.214.50:4840/BFCGateway"
START_NODE = "ns=2;s=Sinumerik.PLC.StartNC"
STOP_NODE = "ns=2;s=Sinumerik.PLC.StopNC"
RESET_NODE = "ns=2;s=Sinumerik.PLC.ResetNC"
PROG_STATUS_NODE = "ns=2;s=Sinutrain.production.progStatus"
NC_RESET_COUNTER_NODE = "ns=2;s=Sinutrain.production.NcResetCounter"
OPC_USER = "admin"
OPC_PASSWORD = "Admin-123"


class OPCClient:
    def __init__(self):
        self.client = None

    def connect(self):
        try:
            self.client = Client(OPC_URL)
            self.client.set_user(OPC_USER)
            self.client.set_password(OPC_PASSWORD)
            self.client.connect()
            return True
        except Exception as e:
            print(f"OPC Connection Error: {e}")
            return False

    def disconnect(self):
        if self.client:
            self.client.disconnect()
            self.client = None

    def send_signal(self, node_id, value=True):
        if not self.client:
            if not self.connect():
                return False
        try:
            node = self.client.get_node(node_id)
            node.set_value(value)
            print(f"Signal sent to {node_id}: {value}")
            return True
        except Exception as e:
            print(f"Signal Error: {e}")
            self.disconnect()
            return False

    def read_value(self, node_id):
        if not self.client:
            if not self.connect():
                return None
        try:
            node = self.client.get_node(node_id)
            return node.get_value()
        except Exception as e:
            print(f"OPC Read Error: {e}")
            self.disconnect()
            return None


opc = OPCClient()

prev_prog_status = None
prev_reset_counter = None
scheduled_start_time = None  # Track delayed start

while True:
    current_prog_status = opc.read_value(PROG_STATUS_NODE)
    current_reset_counter = opc.read_value(NC_RESET_COUNTER_NODE)

    if current_prog_status is None or current_reset_counter is None:
        time.sleep(0.1)
        continue

    # Handle Start/Stop based on progStatus changes
    if current_prog_status != prev_prog_status:
        if current_prog_status == 3:
            # Schedule start after 2 seconds
            scheduled_start_time = time.time()
        elif current_prog_status == 2:
            opc.send_signal(STOP_NODE)
        prev_prog_status = current_prog_status

    # Check delayed start condition
    if scheduled_start_time is not None:
        if current_prog_status == 3 and (time.time() - scheduled_start_time) >= 2:
            opc.send_signal(START_NODE)
            scheduled_start_time = None  # Reset after triggering
        elif current_prog_status != 3:
            # Cancel scheduled start if status changed
            scheduled_start_time = None

    # Handle Reset when progStatus is 5 and counter increments
    if prev_reset_counter is not None:
        if current_prog_status == 5 and current_reset_counter > prev_reset_counter:
            opc.send_signal(RESET_NODE)
            prev_reset_counter = current_reset_counter
    else:
        prev_reset_counter = current_reset_counter

    time.sleep(0.05)
