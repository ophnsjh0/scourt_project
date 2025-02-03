# aci-ep-interface

Retreives endpoints with relevant interfaces

## Table of Contents

- [Prerequisite](#prerequisite)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Credits](#credits)

## Prerequisite

- Python 3.x
- Cisco APIC 5.2(8e) or later

## Installation

for Debian, Ubuntu

```
apt update
apt install python3 python3-pip
pip install -r requirements.txt
```

## Usage

```
usage: aci-ep-interface.py [-h] [-m MANDATORY]

options:
  -h, --help            show this help message and exit
  -m MANDATORY, --mandatory MANDATORY
                        The output includes only the fields separated by commas that have values.
```

## Usage - Examples

```
export ACI_USERNAME="admin"
export ACI_PASSWORD="C1sco12345"
export ACI_URL="https://198.18.133.200"
export ACI_SSLVERIFY=False

# default usage
python aci-ep-interface.py

# show only rows that contain values for both IP address and physical interface
python aci-ep-interface.py -m addr,physIf

# filtering outputs by grep
python aci-ep-interface.py | grep '192.168.10.'
```

## License

TBU

## Credits

- In Seob Kim (insekim@cisco.com)
