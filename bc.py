import sys

if sys.version_info < (3, 6):
    print("Error: This script requires Python 3.6 or later.")
    sys.exit(1)

import argparse
import ipaddress
import os
from abc import ABC, abstractmethod

class LineParser(ABC):
    def __init__(self, strip_ipv6=False):
        self.strip_ipv6 = strip_ipv6

    @abstractmethod
    def parse_line(self, line):
        pass

class LineFormatter(ABC):
    @abstractmethod
    def format_line(self, parsed_line):
        pass

class ParsedLine:
    def __init__(self, label, ip1, ip2, ddd):
        self.label = label
        self.ip1 = ip1
        self.ip2 = ip2
        self.ddd = ddd

    def __repr__(self):
        return (f"ParsedLine(label={self.label}, ip1={self.ip1}, "
                f"ip2={self.ip2}, ddd={self.ddd})")
    
def normalize_ip(ip):
    try:
        if '.' in ip:
            ip = '.'.join(str(int(octet)) for octet in ip.split('.'))
        normalized_ip = ipaddress.ip_address(ip)
        return str(normalized_ip)
    
    except ValueError:
        raise ValueError(f"Invalid IP address: {ip}")

class P2PParser(LineParser):
    def parse_line(self, line):
        line = line.strip()

        if not line or line.startswith("#"):
            return None

        split_line = line.rsplit('-', 1)
        if len(split_line) != 2:
            return None
        
        label_and_ip1 = split_line[0]
        ip2 = split_line[1]
        
        if ':' not in ip2:
            label_ip1_split = label_and_ip1.rsplit(':', 1)
            if len(label_ip1_split) != 2:
                return None
            label = label_ip1_split[0]
            ip1 = label_ip1_split[1]

            try:
                ip1_normalized = normalize_ip(ip1)
                ip2_normalized = normalize_ip(ip2)
            except ValueError:
                return None
        else:
            remaining = label_and_ip1
            while remaining:
                label_ip1_split = remaining.split(':', 1)
                if len(label_ip1_split) != 2:
                    return None

                label_candidate = label_ip1_split[0]
                ip1_candidate = label_ip1_split[1]

                try:
                    ip1_normalized = normalize_ip(ip1_candidate)
                    label = label_candidate
                    break
                except ValueError:
                    if ':' not in ip1_candidate:
                        return None
                    remaining = label_candidate + ':' + ip1_candidate.split(':', 1)[1]

            try:
                ip2_normalized = normalize_ip(ip2)
            except ValueError:
                return None
            
            if self.strip_ipv6:
                return None

        return ParsedLine(label, ip1_normalized, ip2_normalized, "000")

class DATParser(LineParser):
    def parse_line(self, line):
        line = line.strip()
        
        if not line or line.startswith("#"):
            return None

        parts = line.split(',', 2)
        if len(parts) != 3:
            return None
        
        ip_part, ddd_part, label = [part.strip() for part in parts]
        
        ip1, ip2 = map(str.strip, ip_part.split('-', 1))
        if len(ip1) == 0 or len(ip2) == 0:
            return None

        try:
            ip1_normalized = normalize_ip(ip1)
            ip2_normalized = normalize_ip(ip2)
        except ValueError:
            return None
        
        if self.strip_ipv6 and ':' in ip1_normalized:
            return None
        
        if not (ddd_part.isdigit() and len(ddd_part) == 3):
            return None

        ddd = ddd_part
        
        return ParsedLine(label, ip1_normalized, ip2_normalized, ddd)
    
class DATFormatter(LineFormatter):
    def format_line(self, parsed_line):
        if parsed_line is None:
            return ""
        return f"{parsed_line.ip1} - {parsed_line.ip2} , {parsed_line.ddd} , {parsed_line.label}"
    
class P2PFormatter(LineFormatter):
    def format_line(self, parsed_line):
        if parsed_line is None:
            return ""
        return f"{parsed_line.label}:{parsed_line.ip1}-{parsed_line.ip2}"

def get_parser_and_formatter(input_file, strip_ipv6):
    input_ext = os.path.splitext(input_file)[1].lower()
    if input_ext == '.p2p':
        return P2PParser(strip_ipv6), DATFormatter(), os.path.splitext(input_file)[0] + '.dat'
    elif input_ext == '.dat':
        return DATParser(strip_ipv6), P2PFormatter(), os.path.splitext(input_file)[0] + '.p2p'
    else:
        raise ValueError(f"Unsupported input file format: {input_ext}")

def parse_and_convert_file(input_filename, output_filename, parser, formatter):
    try:
        ipv6_bypass_count = 0
        with open(input_filename, 'r', encoding='utf-8') as infile, open(output_filename, 'w', encoding='utf-8') as outfile:
            for line in infile:
                parsed_line = parser.parse_line(line)
                if parsed_line:
                    formatted_line = formatter.format_line(parsed_line)
                    if formatted_line:
                        outfile.write(f"{formatted_line}\n")
                elif parser.strip_ipv6:
                    ipv6_bypass_count += 1
                else:
                    print(f"Failed to parse line: {line.strip()}")

        if parser.strip_ipv6:
            print(f"Stripped {ipv6_bypass_count} lines with ipv6 adresses.")
    except UnicodeDecodeError as e:
        print(f"Error reading file {input_filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Parse and convert files based on format.")
    
    parser.add_argument(
        '--input_file', 
        type=str, 
        required=True, 
        help="The input file to parse."
    )
    
    parser.add_argument(
        '--strip_ipv6', 
        action='store_true', 
        help="Strip IPv6 addresses from the output file."
    )

    args = parser.parse_args()

    input_file = args.input_file
    strip_ipv6 = args.strip_ipv6

    try:
        file_parser, file_formatter, output_file = get_parser_and_formatter(input_file, strip_ipv6)
        parse_and_convert_file(input_file, output_file, file_parser, file_formatter)
        print(f"Processing completed. Output saved to: {output_file}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
