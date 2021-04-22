import json
import binascii
import os


class Device:
    def __init__(self, id_device, name, size, bricks, node):
        if id_device is None:
            self.id_device = binascii.b2a_hex(os.urandom(16)).decode("utf-8")
        else:
            self.id_device = id_device

        self.device = {
            id_device: {
                "State": "online",
                "Info": {
                    "name": name,
                    "storage": {
                        "total": size,
                        "free": size,
                        "used": 0
                    },
                    "id": id_device
                },
                "Bricks": bricks,
                "NodeId": node,
                "ExtentSize": 4096
            }
        }

    def deserialize(self, device):
        self.device = json.loads(device)
        self.id_device = list(self.device.keys())[0]
