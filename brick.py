import os
import binascii
import json


class Brick:
    """Класс для хранения объекта brick"""
    PoolMetadataSize = {1048576: 8192, 2097152: 12288, 3145728: 16384, 4194304: 24576, 5242880: 28672, 6291456: 32768,
                        10485760: 53248, 15728640: 81920}

    def __init__(self, device=None, node=None, volume=None, size=None, id_brick=None):
        if id_brick is None:
            self.id_brick = binascii.b2a_hex(os.urandom(16)).decode("utf-8")
        else:
            self.id_brick = id_brick

        if device is None:
            self.get_volume_group()

        self.brick = {self.id_brick: {"Info": {
            "id": self.id_brick,
            "path": "/var/lib/heketi/mounts/vg_" + device + "/brick_" + self.id_brick + "/brick ",
            "device": device,
            "node": node,
            "volume": volume,
            "size": size
        },
            "TpSize": size,
            "PoolMetadataSize": self.PoolMetadataSize[size],
            "Pending": {
                "Id": ""
            },
            "LvmThinPool": "tp_" + self.id_brick,
            "LvmLv": "",
            "SubxType": 1}
        }

    def get_volume_group(self):
        # TODO get: id_device by node object
        # Текущее возвращаемое знвчение случайно и в реальных условиях работать не будет
        return binascii.b2a_hex(os.urandom(16)).decode("utf-8")

    def serialize(self):
        return json.dumps(self.brick)

    def deserialize(self):
        pass