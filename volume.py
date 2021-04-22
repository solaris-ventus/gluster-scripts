import json
import binascii


class Volume:
    def __init__(self, id_volume=None, size=None, replica=None, id_cluster=None, hosts=None, main_server=None, bricks=()):
        if id_volume is None:
            self.id_volume = binascii.b2a_hex(os.urandom(16)).decode("utf-8")
        else:
            self.id_volume = id_volume
        self.hosts = hosts
        self.main_server = main_server
        self.volume = {id_volume: {
            "Info": {
                "size": size,
                "name": "vol_" + id_volume,
                "durability": {
                    "type": "replicate",
                    "replicate": {
                        "replica": replica
                    },
                    "disperse": {}
                },
                "gid": 2001,
                "snapshot": {
                    "enable": True,
                    "factor": 1
                },
                "id": id_volume,
                "cluster": id_cluster,
                "mount": {
                    "glusterfs": {
                        "hosts": hosts,
                        "device": main_server + ":vol_" + id_volume,
                        "options": {
                            "backup-volfile-servers": self.backup_servers()
                        }
                    }
                },
                "blockinfo": {}
            },
            "Bricks": bricks,
            "GlusterVolumeOptions": [
                "server.tcp-user-timeout 42",
                ""
            ],
            "Pending": {
                "Id": ""
            }
        }}

    def serialize(self):
        return json.dumps(self.volume)

    def deserialize(self, volume):
        self.volume = json.loads(volume)
        self.id_volume = list(self.volume.keys())[0]
        self.main_server = self.volume[self.id_volume]["Info"]["mount"]["glusterfs"]["device"].split(":")[0]
        self.hosts = self.volume[self.id_volume]["Info"]["mount"]["glusterfs"]["hosts"]

    load = deserialize

    def backup_servers(self):
        return self.hosts.remove(self.main_server)

    def add_replica(self, new_hosts=None, all_hosts=None):
        pass


