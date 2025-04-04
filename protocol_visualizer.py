import argparse as ap
import matplotlib.pyplot as plt

from J1939 import J1939
from protocol import Waveform

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
    if max_time < 1e-6:  # Less than 1 microsecond
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*1e9:.0f}ns'))
    elif max_time < 1e-3:  # Less than 1 millisecond
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*1e6:.0f}µs'))
    elif max_time < 1:  # Less than 1 second
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x*1e3:.0f}ms'))
    else:
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.3f}s'))
        
    plt.show()

# Example usage
if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Visualize protocol waveforms")
    parser.add_argument("data", type=str, help="The data to visualize")
    args = parser.parse_args()

    protocol = J1939()
    
    # Plot the waveform
    plot_waveform(protocol.generate_waveform(args.data), "J1939 Protocol Waveform") 