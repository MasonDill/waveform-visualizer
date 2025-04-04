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

class Waveform:
    def __init__(self, time_points: List[float], voltage_points: List[float]):
        self.time_points = time_points
        self.voltage_points = voltage_points

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
    
    def generate_waveform(self, data: str) -> Waveform:
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
            
        return Waveform(time_points, voltage_points)