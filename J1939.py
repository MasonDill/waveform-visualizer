from protocol import Protocol, Frame, Field, Symbol
from enum import Enum

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
        
class J1939ProbeConfiguration(Enum):
    CAN_H = 0
    CAN_L = 1
    DIFFERENTIAL = 2

class J1939(Protocol):

    def __init__(self, probe_configuration: J1939ProbeConfiguration):
        J1939_FREQUENCY = 250000

        J1939_CAN_H_HIGH_LOGIC_VOLTAGE = 3.5
        J1939_CAN_H_LOW_LOGIC_VOLTAGE = 2.5

        J1939_CAN_L_HIGH_LOGIC_VOLTAGE = 2.5
        J1939_CAN_L_LOW_LOGIC_VOLTAGE = 1.5

        J1939_DIFFERENTIAL_HIGH_LOGIC_VOLTAGE = J1939_CAN_H_HIGH_LOGIC_VOLTAGE - J1939_CAN_L_HIGH_LOGIC_VOLTAGE
        J1939_DIFFERENTIAL_LOW_LOGIC_VOLTAGE = J1939_CAN_H_LOW_LOGIC_VOLTAGE - J1939_CAN_L_LOW_LOGIC_VOLTAGE

        if probe_configuration == J1939ProbeConfiguration.CAN_H:
            high_logic_voltage = J1939_CAN_H_HIGH_LOGIC_VOLTAGE
            low_logic_voltage = J1939_CAN_H_LOW_LOGIC_VOLTAGE
        elif probe_configuration == J1939ProbeConfiguration.CAN_L:
            high_logic_voltage = J1939_CAN_L_HIGH_LOGIC_VOLTAGE
            low_logic_voltage = J1939_CAN_L_LOW_LOGIC_VOLTAGE
        elif probe_configuration == J1939ProbeConfiguration.DIFFERENTIAL:
            high_logic_voltage = J1939_DIFFERENTIAL_HIGH_LOGIC_VOLTAGE
            low_logic_voltage = J1939_DIFFERENTIAL_LOW_LOGIC_VOLTAGE
        else:
            raise ValueError("Invalid probe configuration")

        super().__init__(J1939_FREQUENCY, high_logic_voltage, low_logic_voltage, J1939Frame())