import sys
import ipaddress

def is_ipv6_address(addr):
    try:
        ipaddress.IPv6Address(addr)
        return True
    except ipaddress.AddressValueError:
        return False

def count_ipv6_lines(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            total_count = 0
            for line_number, line in enumerate(file, start=1):
                parts = line.rsplit('-', 1)  # Split on the final '-'
                if len(parts) > 1 and is_ipv6_address(parts[1].strip()):
                    print(f"Line {line_number}: {parts[1].strip()}")
                    total_count += 1
            print(f"Total count of lines with IPv6 addresses: {total_count}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except UnicodeDecodeError:
        print(f"Error: File '{file_path}' could not be decoded as UTF-8.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
    else:
        count_ipv6_lines(sys.argv[1])
