import matplotlib.pyplot as plt
import numpy as np
from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

@dataclass
class Symbol:
    """Represents a single symbol in the protocol (logic level and duration)"""
    logic_level: float
    duration: float

@dataclass
class Field:
    """Represents a field in the protocol frame (e.g., ID, Data, CRC)"""
    name: str
    length: int
    symbols: List[Symbol]

    def __init__(self, name: str, length: int, symbols: List[Symbol]=List[Symbol](length)):
        self.name = name
        self.symbols = symbols

    def parse_user_data(self, data: str, frame_start: int) -> List[Symbol]:
        """Parse the user data from the input string into the frame"""
        start_index = frame_start // 4 # each char is 4 bits
        num_chars = self.length // 4 # each char is 4 bits

        if num_chars == 0:
            num_chars = 1
        data = data[frame_start:frame_start+num_chars]
        data_int = int(data, 16)

        for i in range(self.length):
            bit_value = (data_int >> i) & 1
            self.symbols[self.length - i - 1].logic_level = bit_value

class Frame:
    """Represents a complete protocol frame"""
    def __init__(self, fields: List[Field]):
        self.fields = fields
    
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols in the frame in order"""
        symbols = []
        for field in self.fields:
            symbols.extend(field.symbols)
        return symbols
    
    @abstractmethod
    def parse_user_data(self, data: str) -> List[Symbol]:
        """Parse the user data from the input string into the frame"""
        frame_start = 0
        for field in self.fields:
            field.parse_user_data(data, frame_start)
            frame_start += field.length

class Protocol(ABC):
    def __init__(self, frequency: float, high_logic_voltage: float, low_logic_voltage: float, data_frame: Frame):
        self.frequency = frequency
        self.period = 1.0 / frequency
        self.high_logic_voltage = high_logic_voltage
        self.low_logic_voltage = low_logic_voltage
        self.data_frame = data_frame

    def logic_to_voltage(self, logic_level: int) -> float:
        """Convert a logical level (0 or 1) to the corresponding voltage"""
        if logic_level == 1:
            return self.high_logic_voltage
        else:
            return self.low_logic_voltage
    
    def generate_waveform(self, data: str) -> Tuple[List[float], List[float]]:
        """Generate the complete waveform from the frame"""
        # Create the frame
        frame = self.data_frame
        
        # Get all symbols
        symbols = frame.get_all_symbols()
        
        # Generate time and voltage arrays
        time_points = []
        voltage_points = []
        current_time = 0.0
        
        for symbol in symbols:
            time_points.append(current_time)
            voltage_points.append(self.logic_to_voltage(symbol.logic_level))
            current_time += symbol.duration
            
        return time_points, voltage_points
    
    def plot_waveform(self, data: str, title: str = "Protocol Waveform"):
        """Plot the waveform using matplotlib"""
        time_points, voltage_points = self.generate_waveform(data)
        
        plt.figure(figsize=(12, 6))
        plt.plot(time_points, voltage_points, 'b-', linewidth=2)
        plt.grid(True)
        plt.title(title)
        plt.xlabel('Time (s)')
        plt.ylabel('Voltage (V)')
        
        # Format time axis to use appropriate units
        max_time = max(time_points)
        if max_time < 1e-6:  # Less than 1 microsecond
            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*1e9:.0f}ns'))
        elif max_time < 1e-3:  # Less than 1 millisecond
            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*1e6:.0f}µs'))
        elif max_time < 1:  # Less than 1 second
            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*1e3:.0f}ms'))
        else:
            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}s'))
            
        plt.show()

class J1939(Protocol):
    class J1939Sof(Field):
        def __init__(self):
            super().__init__(name="SOF", length=1)
    
    class J1939Id(Field):
        def __init__(self, is_extended: bool):
            field_length = 29 if is_extended else 11
            super().__init__(name="ID", length=field_length)

    class J1939Control(Field):
        def __init__(self):
            super().__init__(name="Control", length=3)
        
    class J1939Data(Field):
        def __init__(self):
            super().__init__(name="Data", length=8)
    
    class J1939Crc(Field):
        def __init__(self):
            super().__init__(name="CRC", length=15)

    class J1939Ack(Field):
        def __init__(self):
            super().__init__(name="ACK", length=2)

    class J1939Eof(Field):
        def __init__(self):
            super().__init__(name="EOF", length=7)

    class J1939Frame(Frame):
        def __init__(self):
            fields = [J1939Sof(), J1939Id(is_extended=False), J1939Control(), J1939Data(), J1939Crc(), J1939Ack(), J1939Eof()]
            super().__init__(fields)

    def __init__(self):
        J1939_FREQUENCY = 250000

        J1939_CAN_H_HIGH_LOGIC_VOLTAGE = 3.5
        J1939_CAN_H_LOW_LOGIC_VOLTAGE = 2.5

        # J1939_CAN_L_HIGH_LOGIC_VOLTAGE = 2.5
        # J1939_CAN_L_LOW_LOGIC_VOLTAGE = 1.5

        super().__init__(J1939_FREQUENCY, J1939_CAN_H_HIGH_LOGIC_VOLTAGE, J1939_CAN_H_LOW_LOGIC_VOLTAGE, J1939Frame())
        
    def create_frame(self, data: str) -> Frame:
        """Create a J1939 frame from the input data"""
        fields = []
        
        # Initial state (5 periods of low)
        initial_field = Field(
            name="Initial State",
            symbols=[Symbol(voltage=self.low_logic_voltage, duration=self.period, name="Initial")] * 5,
            description="Initial state before frame starts"
        )
        fields.append(initial_field)
        
        # Start of Frame
        sof_field = Field(
            name="SOF",
            symbols=[Symbol(voltage=self.high_logic_voltage, duration=self.period, name="SOF")],
            description="Start of Frame marker"
        )
        fields.append(sof_field)
        
        # Create DataFrame
        self.data_segment = DataFrame(data)
        print(f"Data length: {self.data_segment.get_binary_length()} bits")
        
        # Data field
        data_field = Field(
            name="Data",
            symbols=self.data_segment.get_symbols(self),
            description="Message data"
        )
        fields.append(data_field)
        
        # End of Frame
        eof_field = Field(
            name="EOF",
            symbols=[Symbol(voltage=self.low_logic_voltage, duration=self.period, name="EOF")],
            description="End of Frame marker"
        )
        fields.append(eof_field)
        
        return Frame(fields)

# Example usage
if __name__ == "__main__":
    protocol = J1939()
    
    # Example J1939 message (simplified for demonstration)
    # Format: ID (11 bits) + Control (3 bits) + Data (64 bits) + CRC (15 bits) + ACK (2 bits)
    example_data = "0x18FF00F0"  # Example message ID and data
    
    # Plot the waveform
    protocol.plot_waveform(example_data, "J1939 Protocol Waveform") 