# IP Blocklist Converter

This Python script converts IP blocklists between `p2p` and `dat` formats.

## Requirements

- Python 3.6 or later

## Usage

To use the script, open a terminal and navigate to the directory where the script is stored. You can then run the script using the following command:

```bash
python ./bc.py --input_file <input_file_path> [--strip_ipv6]
```

### Arguments

- `--input_file <input_file_path>`: The path to the input file. The script will automatically determine the file format (either `p2p` or `dat`) and convert it to the other format.
- `--strip_ipv6`: (Optional) Use this flag if your application cannot parse IPv6 addresses. This will remove IPv6 addresses from the output file.

### Examples

**Convert a `p2p` file to `dat` format:**

```bash
python ./bc.py --input_file path/to/input.p2p
```

**Convert a `dat` file to `p2p` format and strip IPv6 addresses:**

```bash
python ./bc.py --input_file path/to/input.dat --strip_ipv6
```

## Notes

- The script will handle the conversion based on the file extension of the input file.
- If `--strip_ipv6` is used, IPv6 addresses will be removed from the output file to ensure compatibility with applications that do not support them.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
