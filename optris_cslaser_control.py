import serial
import logging
from typing import Optional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BAUDRATE = 9600
DATA_BITS = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
FLOW_CONTROL = serial.XONXOFF
TIMEOUT = 1.0


class OptrisCSLaserControl:
    def __init__(self, port: str, baudrate: int = BAUDRATE, timeout:float = TIMEOUT):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None


    def connect(self):
        if not self.serial or not self.serial.is_open:
            try:
                self.serial = serial.Serial(
                    port=self.port, baudrate=self.baudrate, timeout=self.timeout, bytesize=DATA_BITS,
                    parity=PARITY, stopbits=STOP_BITS, xonxoff=FLOW_CONTROL)
                logging.info(f"Connected to Optris CS Laser on {self.port}.")
            except serial.SerialException as e:
                logging.error(f"Failed to connect to Optris CS Laser: {e}")


    def disconnect(self):
        if self.serial is None:
            logging.warning("No serial connection to disconnect.")
            return
        if self.serial.is_open:
            try:
                self.serial.close()
                self.serial = None
                logging.info("Disconnected from Optris CS Laser.")
            except serial.SerialException as e:
                logging.error(f"Failed to disconnect from Optris CS Laser: {e}")


    def __del__(self):
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
                self.serial = None
            except serial.SerialException as e:
                logging.error(f"Failed to close serial connection: {e}")
        logging.info("OptrisCSLaserControl instance deleted.")


    def send_command(self, hex_command: str) -> None:
        if self.serial is None:
            logging.warning("No serial connection established. Cannot send command.")
            return
        if self.serial.is_open:
            self.serial.write(hex_command.encode('utf-8'))
            logging.info(f"Sending command: {hex_command}")
    

    def read_response(self, read_bytes: int) -> Optional[str]:
        if self.serial is None:
            return None
        if self.serial.is_open:
            try:
                return self.serial.read(read_bytes)
            except serial.SerialException as e:
                logging.error(f"Failed to read response: {e}")
                return None
    
    @property
    def serial_number(self) -> Optional[int]:
        """
        HEX command: 0x0E
        Answer format: 3 bytes
        """
        hex_command = b'\x0E'
        self.send_command(hex_command)
        res = self.read_response(3)
        try:
            byte1, byte2, byte3 = res[0], res[1], res[2]
            return byte1 * 65536 + byte2 * 256 + byte3
        except (TypeError, IndexError) as e:
            logging.error(f"Failed to parse serial number: {e}")
            return None
    

    @property
    def target_temperature(self) -> Optional[float]:
        """
        HEX command: 0x01
        Answer format: 2 bytes (Celsius)
        """
        hex_command = b'\x01'
        self.send_command(hex_command)
        res = self.read_response(2)
        try:
            byte1, byte2 = res[0], res[1]
            return (byte1 * 256 + byte2 - 1000) / 10.0
        except (TypeError, IndexError) as e:
            logging.error(f"Failed to parse target temperature: {e}")
            return None
    

    @property
    def head_temperature(self) -> Optional[float]:
        """
        HEX command: 0x02
        Answer format: 2 bytes (Celsius)
        """
        hex_command = b'\x02'
        self.send_command(hex_command)
        res = self.read_response(2)
        try:
            byte1, byte2 = res[0], res[1]
            return (byte1 * 256 + byte2 - 1000) / 10.0
        except (TypeError, IndexError) as e:
            logging.error(f"Failed to parse head temperature: {e}")
            return None
    

    @property
    def current_target_temperature(self) -> Optional[float]:
        """
        HEX command: 0x03
        Answer format: 2 bytes (Celsius)
        """
        hex_command = b'\x03'
        self.send_command(hex_command)
        res = self.read_response(2)
        try:
            byte1, byte2 = res[0], res[1]
            return (byte1 * 256 + byte2 - 1000) / 10.0
        except (TypeError, IndexError) as e:
            logging.error(f"Failed to parse current target temperature: {e}")
            return None
    

    @property
    def emissivity(self) -> Optional[float]:
        """
        HEX command: 0x04
        Answer format: 2 bytes (0.01 steps)
        """
        hex_command = b'\x04'
        self.send_command(hex_command)
        res = self.read_response(2)
        try:
            byte1, byte2 = res[0], res[1]
            return (byte1 * 256 + byte2) / 1000.0
        except (TypeError, IndexError) as e:
            logging.error(f"Failed to parse emissivity: {e}")
            return None
    

    @emissivity.setter
    def emissivity(self, new_emissivity: float) -> None:
        """
        HEX command: 0x84
        Example: send 84 03 B6 -> Receive 03 B6
        03B6 = dec. 950 -> 0.95
        """
        hex_value = hex(int(new_emissivity * 1000))[2:].zfill(4)
        hex_command = bytes.fromhex('84' + hex_value)
        self.send_command(hex_command)
        res = self.read_response(2)
        try:
            byte1, byte2 = res[0], res[1]
            if (byte1 * 256 + byte2) != int(new_emissivity * 1000):
                logging.error("Failed to set emissivity correctly.")
                return
        except (TypeError, IndexError) as e:
            logging.error(f"Failed to parse response after setting emissivity: {e}")
            return
        logging.info(f"Set emissivity to {new_emissivity}.")
    

    @property
    def laser(self) -> Optional[bool]:
        """
        HEX command: 0x10
        Answer format: 1 byte (0x00 = off, 0x01 = on)
        """
        hex_command = b'\x10'
        self.send_command(hex_command)
        res = self.read_response(1)
        try:
            return res[0] == 1
        except (TypeError, IndexError) as e:
            logging.error(f"Failed to parse laser state: {e}")
            return None
    

    @laser.setter
    def laser(self, state: bool) -> None:
        """
        HEX command: 0x90
        Example: send 90 01 -> Receive 01 (turn on)
        01 = on, 00 = off
        """
        hex_value = '01' if state else '00'
        hex_command = bytes.fromhex('90' + hex_value)
        self.send_command(hex_command)
        res = self.read_response(1)
        try:
            if res[0] != (1 if state else 0):
                logging.error("Failed to set laser state correctly.")
                return
        except (TypeError, IndexError) as e:
            logging.error(f"Failed to parse response after setting laser state: {e}")
            return
        logging.info(f"Set laser state to {'on' if state else 'off'}.")
