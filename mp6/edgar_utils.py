import pandas as pd
import re
import netaddr
from bisect import bisect_left

# Load and preprocess the IP to location data
ips_df = pd.read_csv("ip2location.csv")
ips_df = ips_df.sort_values('low').reset_index(drop=True)
ips_df['low'] = ips_df['low'].apply(lambda x: int(netaddr.IPAddress(x)))
ips_df['high'] = ips_df['high'].apply(lambda x: int(netaddr.IPAddress(x)))

def lookup_region(ip_addr):
    # Replace any letters with "0" to handle anonymized IPs
    clean_ip = re.sub(r'[a-zA-Z]', '0', ip_addr)
    # Convert the cleaned IP to an integer
    ip_int = int(netaddr.IPAddress(clean_ip))
    
    # Perform binary search to find the index
    idx = bisect_left(ips_df['low'].values, ip_int)
    
    # Adjust the index if necessary
    if idx < len(ips_df) and ips_df['low'].iloc[idx] <= ip_int <= ips_df['high'].iloc[idx]:
        return ips_df['region'].iloc[idx]
    elif idx > 0 and ips_df['low'].iloc[idx - 1] <= ip_int <= ips_df['high'].iloc[idx - 1]:
        return ips_df['region'].iloc[idx - 1]
    else:
        return "Unknown"

# class Filing:
#     def __init__(self, html):
#         self.dates = re.findall(r"\b(?:19|20)\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])\b", html)
        
#         sic_match = re.search(r"SIC=(\d+)", html)
#         self.sic = int(sic_match.group(1)) if sic_match else None
        
#         self.addresses = []
#         for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
#             lines = []
#             for line in re.findall(r'<span class="mailerAddress">(.*?)</span>', addr_html):
#                 lines.append(line.strip())
#             self.addresses.append("\n".join(lines))
    
#     def state(self):
#         for address in self.addresses:
#             match = re.search(r"\b([A-Z]{2})\b(?:\s\d{5})?", address)
#             if match:
#                 print(f"State found: {match.group(1)}")
#                 return match.group(1)
            
#         return None

class Filing:
    def __init__(self, html):
        # Extract dates in YYYY-MM-DD format
        self.dates = re.findall(r"\b(?:19|20)\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])\b", html)
        
        # Extract SIC code
        sic_match = re.search(r"SIC=(\d+)", html)
        self.sic = int(sic_match.group(1)) if sic_match else None
        
        # Extract addresses by capturing all <span class="mailerAddress"> elements within <div class="mailer">
        self.addresses = []
        for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
            # Capture all <span class="mailerAddress"> elements
            full_address = []
            for line in re.findall(r'<span class="mailerAddress">([\s\S]*?)</span>', addr_html):
                # Strip each line and append to the full address
                stripped_line = line.strip()
                if stripped_line:
                    full_address.append(stripped_line)
            # Join all parts of the address and store it
            if full_address:
                self.addresses.append("\n".join(full_address))
    
    def state(self):
        for address in self.addresses:
            # Look for patterns of state abbreviations (2 capital letters) followed by a 5-digit ZIP code
            match = re.search(r"\b([A-Z]{2})\s\d{5}\b", address)
            if match:
                return match.group(1)  # Return the state abbreviation
        
        return None  # If no valid state pattern is found, return None

