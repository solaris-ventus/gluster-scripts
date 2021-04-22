import json
import binascii


class Node:
    def __init__(self, id_node=None, hostname=None, ip=None, cluster=None, devices=None):
        if id_node is None:
            self.id_node = binascii.b2a_hex(os.urandom(16)).decode("utf-8")
        else:
            self.id_node = id_node
        self.node = {self.id_node: {
            "State": "online",
            "Info": {
                "zone": 1,
                "hostnames": {
                    "manage": [
                        hostname
                    ],
                    "storage": [
                        ip
                    ]
                },
                "cluster": cluster,
                "id": id_node
            },
            "Devices": devices
        }}

    def serialize(self):
        self.node

