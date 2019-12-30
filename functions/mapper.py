# -*- coding: utf-8 -*-
import json
import oss2
from enum import Enum

oss_endpoint = "oss-cn-beijing-internal.aliyuncs.com"
oss_bucket = "demo-etl"
intermediate_result_prefix = "map_%s"


class ErrorCodes(Enum):
    # common error codes
    StatusSuccess = "operation success"

    # for mapping
    OSSPushObjectFailed = "push result to oss failed"


class ErrorNeedsRetry(Exception):
    pass


class Mapper:
    """
    Mapping operation class
    """
    def __init__(self, context, shard_id, shard_data):
        """
        :param context: fc input context, used for getting credential.
        :param shard_id: shard id to be dealt
        :param shard_data: data to be dealt
        """
        creds = context.credentials
        self.mapping_result_file = intermediate_result_prefix % shard_id
        auth = oss2.StsAuth(creds.access_key_id, creds.access_key_secret, creds.security_token)
        self.bucket = oss2.Bucket(auth, oss_endpoint, oss_bucket)
        self.data = shard_data
        self.mapping_result = {}

    def process(self):
        """ process data.
        :return:
        """
        for data in self.data:
            if data in self.mapping_result.keys():
                self.mapping_result[data] += 1
            else:
                self.mapping_result[data] = 1
        return

    def persist(self):
        """ touch file in oss. True will be returned if operation succeeded.
        :return: bool
        """
        resp = self.bucket.put_object(self.mapping_result_file, json.dumps(self.mapping_result))
        return resp.status == 200


def handler(event, context):
    evt = json.loads(event)
    shard = evt["shard"]

    mapper = Mapper(context, shard["id"], shard["data"])

    # start mapping data processing
    mapper.process()

    # save to oss bucket
    if not mapper.persist():
        raise ErrorNeedsRetry(ErrorCodes.OSSPushObjectFailed.value)

    return json.dumps({"MappingStatus": ErrorCodes.StatusSuccess.value})


