# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import json
import sys
import os
import argparse
import random

import brick
import volume
import node
import device


class Reverse:
    """Iterator for looping over a sequence backwards."""

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        for index in range(len(self.data)):
            yield self.data[index]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', action='store', default='heketi-dump.json')
    parser.add_argument('--output', action='store', default='heketi-dump-new.json')
    args = parser.parse_args()
    heketi_dump_file = open(args.file, 'r')
    heketi_dump_new_file = open(args.output, 'w')
    heketi_object = json.load(heketi_dump_file)

    hosts = ["172.28.124.184", "172.28.124.185", "172.28.124.186", "172.28.124.187"]
    nodes = heketi_object["nodeentries"].keys()

    CScript = open('create_script.sh', 'a')
    CScript.truncate(0)

    brickaddScript = open("add-brick.sh", 'a')
    brickaddScript.truncate(0)

    # Правим volume'ы с 2 brcik'ами
    for key_volume in heketi_object["volumeentries"]:
        if heketi_object["volumeentries"][key_volume]["Info"]["durability"]["replicate"]["replica"] == 2 \
                and len(heketi_object["volumeentries"][key_volume]["Bricks"]) == 2:
            # Добавляем все возможные хосты.
            heketi_object["volumeentries"][key_volume]["Info"]["mount"]["glusterfs"]["hosts"].extend(hosts)
            # Уникальность (list -> set -> list)
            heketi_object["volumeentries"][key_volume]["Info"]["mount"]["glusterfs"]["hosts"] = \
                list(set(heketi_object["volumeentries"][key_volume]["Info"]["mount"]["glusterfs"]["hosts"]))
            # Основной сервер монтиорование
            main_server = heketi_object["volumeentries"][key_volume]["Info"]["mount"]["glusterfs"]["device"].split(":")[0]
            # Создаем копию списка всех хостов
            new_backup = list(hosts)
            # Удаляем из этого списка основной сервер монтирование, полчаем на выходе список backup серверов
            new_backup.remove(main_server)
            # Обновляем строку с backup серверами
            heketi_object["volumeentries"][key_volume]["Info"]["mount"]["glusterfs"]["options"]["backup-volfile-servers"] = \
                ','.join(new_backup)
            # Обновляем количество реплик
            heketi_object["volumeentries"][key_volume]["Info"]["durability"]["replicate"]["replica"] = 3

            # Список brick для volume
            bricks_of_volume = {key_brick: heketi_object["brickentries"][key_brick]
                                for key_brick in heketi_object["brickentries"]
                                if heketi_object["brickentries"][key_brick]["Info"]["volume"] == key_volume}

            # Узлы на которых располагется brick'и volume'а
            nodes_of_volume = list((bricks_of_volume[key_brick]["Info"]["node"] for key_brick in bricks_of_volume))

            # Доступные узлы
            available_node = list((node for node in list(heketi_object["nodeentries"].keys())
                                   if node not in nodes_of_volume))
            # Если в доступных узлах есть toswrkr2 - удалить
            try:
                available_node.remove("6622e5d6546408f4c66e2844fad2c4f1")
            except ValueError:
                pass

            size_new_brick = bricks_of_volume[next(iter(bricks_of_volume))]["Info"]["size"]
            node_for_new_brick = random.choice(available_node)
            device_for_new_brick = random.choice(heketi_object["nodeentries"][node_for_new_brick]["Devices"])
            new_brick = brick.Brick(node=node_for_new_brick, volume=key_volume, size=size_new_brick,
                                    device=device_for_new_brick)
            heketi_object["brickentries"].update(new_brick.brick)
            heketi_object["volumeentries"][key_volume]["Bricks"].append(new_brick.id_brick)
            heketi_object["deviceentries"][device_for_new_brick]["Bricks"].append(new_brick.id_brick)

            # Отладка для отслеживания распределния по нодам
            for x in new_brick.brick:
                print(new_brick.brick[x]["Info"]["node"])

            CScript.write("ssh " + heketi_object["nodeentries"][node_for_new_brick]["Info"]["hostnames"]["manage"][0] +
                  " lvcreate --thinpool vg_" + device_for_new_brick + "/tp_" + next(iter(new_brick.brick)) +
                  " --size " + str(size_new_brick) + "k --chunksize 256k --poolmetadatasize " +
                  str(brick.Brick.PoolMetadataSize[size_new_brick]) + "k --zero n\n")

            CScript.write("ssh " + heketi_object["nodeentries"][node_for_new_brick]["Info"]["hostnames"]["manage"][0] +
            " lvcreate --thin --name brick_" + next(iter(new_brick.brick)) + " --virtualsize " + str(size_new_brick) +
            "k vg_" + device_for_new_brick + "/tp_" + next(iter(new_brick.brick)) + "\n")

            CScript.write("ssh " + heketi_object["nodeentries"][node_for_new_brick]["Info"]["hostnames"]["manage"][0] +
                  " mkfs.xfs -f -i size=512 -n size=8192 -d su=128k,sw=10 /dev/vg_" + device_for_new_brick +
                  "/brick_" + next(iter(new_brick.brick)) + "\n")

            brickaddScript.write(" gluster volume add-brick vol_" + key_volume + " replica 3 " +
                          heketi_object["nodeentries"][node_for_new_brick]["Info"]["hostnames"]["storage"][0] +
                          ":" + new_brick.brick[next(iter(new_brick.brick))]["Info"]["path"] + "\n")

    json.dump(heketi_object, heketi_dump_new_file, indent=2)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
