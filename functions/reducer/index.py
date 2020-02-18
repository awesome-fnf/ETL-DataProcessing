# -*- coding: utf-8 -*-
import json
import oss2
import os
from enum import Enum

intermediate_result_prefix = "map_%s"
final_result = "reduced_result"

class ErrorCodes(Enum):
    # common error codes
    StatusSuccess = "operation success"

    # for reducing
    OSSGetObjectFailed = "get mapping result to oss failed"
    OSSPushObjectFailed = "push result to oss failed"


class ErrorNeedsRetry(Exception):
    pass


class Reducer:
    """
    reducing operation class
    """

    def __init__(self, context, shard_ids):
        """
        :param context: fc input context, used for getting credential.
        :param shard_ids: total shards
        """
        creds = context.credentials
        self.shard_ids = shard_ids
        auth = oss2.StsAuth(creds.access_key_id, creds.access_key_secret, creds.security_token)
        endpoint = 'https://oss-%s-internal.aliyuncs.com' % context.region
        oss_bucket = os.environ["BucketName"]
        self.bucket = oss2.Bucket(auth, endpoint, oss_bucket)
        self.intermediate_result = []
        self.final_result = {}

    def fetch_mapping_result(self):
        """
        :return: bool
        """
        for shard_id in self.shard_ids:
            try:
                object_stream = self.bucket.get_object(intermediate_result_prefix % shard_id)
                file_content = object_stream.read()
                self.intermediate_result.append(json.loads(file_content))
            except oss2.exceptions.NoSuchKey:
                return False
            except json.decoder.JSONDecodeError:
                # data crash
                return False
        return True

    def reducing(self):
        """
        :return: None
        """
        for data in self.intermediate_result:
            for data_type in data:
                if data_type in self.final_result.keys():
                    self.final_result[data_type] += data[data_type]
                else:
                    self.final_result[data_type] = data[data_type]
        return

    def persist(self):
        """ touch file in oss. True will be returned if operation succeeded.
        :return: bool
        """
        resp = self.bucket.put_object(final_result, json.dumps(self.final_result))
        return resp.status == 200


def handler(event, context):
    evt = json.loads(event)

    shard_ids = evt["shard_ids"]
    reducer = Reducer(context, shard_ids)

    # receive map result
    if not reducer.fetch_mapping_result():
        raise ErrorNeedsRetry(ErrorCodes.OSSGetObjectFailed.value)

    # reducing
    reducer.reducing()

    # save to oss bucket
    if not reducer.persist():
        raise ErrorNeedsRetry(ErrorCodes.OSSPushObjectFailed.value)

    return json.dumps({"ReducingStatus": ErrorCodes.StatusSuccess.value})
