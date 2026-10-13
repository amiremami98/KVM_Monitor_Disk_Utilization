#!/usr/bin/env python3
# Usage: python3 monitor_disk.py <vm_name> <device_name>
import subprocess
import time
import sys

def get_stats(vm, dev):
    """
    Run virsh domblkstat and parse the cumulative output.
    """
    out = subprocess.check_output(['virsh', 'domblkstat', vm, dev], text=True)
    stats = {}
    for line in out.strip().split('\n'):
        parts = line.split()
        if len(parts) == 3:
            stats[parts[1]] = int(parts[2])
    return stats

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 monitor_disk.py <vm_name> <device>")
        sys.exit(1)
        
    vm, dev = sys.argv[1], sys.argv[2]
    prev_stats = get_stats(vm, dev)
    
    # Updated header to include IOPS columns
    header = f"{'R-BW (KB/s)':<15} | {'W-BW (KB/s)':<15} | {'R-IOPS':<10} | {'W-IOPS':<10} | {'R-Lat (ms)':<12} | {'W-Lat (ms)':<12}"
    print(header)
    print("-" * len(header))
    
    try:
        while True:
            time.sleep(1)
            curr_stats = get_stats(vm, dev)
            
            # Deltas (Difference between current and previous stats)
            d_rd_bytes = curr_stats.get('rd_bytes', 0) - prev_stats.get('rd_bytes', 0)
            d_wr_bytes = curr_stats.get('wr_bytes', 0) - prev_stats.get('wr_bytes', 0)
            
            # The delta of requests over 1 second represents the IOPS
            d_rd_req = curr_stats.get('rd_req', 0) - prev_stats.get('rd_req', 0)
            d_wr_req = curr_stats.get('wr_req', 0) - prev_stats.get('wr_req', 0)
            
            d_rd_time = curr_stats.get('rd_total_times', 0) - prev_stats.get('rd_total_times', 0)
            d_wr_time = curr_stats.get('wr_total_times', 0) - prev_stats.get('wr_total_times', 0)
            
            # Bandwidth (KB/s)
            rd_bw_kb = d_rd_bytes / 1024
            wr_bw_kb = d_wr_bytes / 1024
            
            # IOPS
            rd_iops = d_rd_req
            wr_iops = d_wr_req
            
            # Latency (ms) - avoiding division by zero
            rd_lat = (d_rd_time / d_rd_req / 1000000.0) if d_rd_req > 0 else 0
            wr_lat = (d_wr_time / d_wr_req / 1000000.0) if d_wr_req > 0 else 0
            
            # Print the formatted row
            print(f"{rd_bw_kb:<15.2f} | {wr_bw_kb:<15.2f} | {rd_iops:<10} | {wr_iops:<10} | {rd_lat:<12.3f} | {wr_lat:<12.3f}")
            
            prev_stats = curr_stats
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
