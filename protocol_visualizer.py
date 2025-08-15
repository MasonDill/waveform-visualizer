import argparse as ap
import matplotlib.pyplot as plt

from J1939 import J1939, J1939ProbeConfiguration
from protocol import Waveform, Protocol

def get_time_formatter(max_time):
    """Returns a formatter function based on the maximum time value"""
    if max_time < 1e-6:  # Less than 1 microsecond
        return lambda x, p: f'{x*1e9:.0f}ns'
    elif max_time < 1e-3:  # Less than 1 millisecond
        return lambda x, p: f'{x*1e6:.0f}µs'
    elif max_time < 1:  # Less than 1 second
        return lambda x, p: f'{x*1e3:.0f}ms'
    else:
        return lambda x, p: f'{x:.3f}s'

def plot_waveform(waveform: Waveform, title: str = "Protocol Waveform"):
    """Plot the waveform using matplotlib"""
    
    plt.figure(figsize=(12, 6))
    plt.plot(waveform.time_points, waveform.voltage_points, 'b-', linewidth=2)
    plt.grid(True)
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    
    # Format time axis to use appropriate units
    max_time = max(waveform.time_points)
    formatter = get_time_formatter(max_time)
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(formatter))
        
    plt.show()

def interactive_entry(protocol: Protocol) -> Waveform:
    mode = input("Hex or Decimal? (h/d): ")
    
    for field in protocol.data_frame.fields:
        field_data = input(f"Enter the data for {field.name}: ")

        if mode == "h":
            field.parse_as_string(field_data)
        elif mode == "d":
            field.parse_as_decimal(int(field_data, 16))
        else:
            raise ValueError("Invalid mode")

    waveform = protocol.generate_waveform()
    return waveform

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Visualize protocol waveforms")
    parser.add_argument("-d", "--data", type=str, help="The data to visualize", required=False)
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    protocol = J1939(J1939ProbeConfiguration.CAN_H)

    waveform = None
    
    if args.interactive:
        waveform = interactive_entry(protocol)
    elif args.data is not None:
        waveform = protocol.generate_waveform(args.data)
    else:
        raise ValueError("No data provided")
    
    plot_waveform(waveform, "J1939 Protocol Waveform") 