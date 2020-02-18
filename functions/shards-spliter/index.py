# -*- coding: utf-8 -*-
import json
import random

# each shard has 3 pieces of data
shard_data_count = 3


def handler(event, context):
    shards = []
    shard_ids = []
    # split data to shards, may get 3-5 pieces of shards
    seed = random.randint(2, 4)
    for shard_num in range(seed):
        shard_name = "shard_%s" % shard_num
        shard_ids.append(shard_name)
        shard_data = {
            "id": shard_name,
            "data": []
        }
        for count in range(shard_data_count):
            data_value = random.randint(1, 2)
            data = "data_%s" % data_value
            shard_data["data"].append(data)
        shards.append(shard_data)

    return json.dumps({'shards': shards, 'shard_ids': shard_ids})
