from boto.connection import AWSAuthConnection
import os

class ESConnection(AWSAuthConnection):

    def __init__(self, region, **kwargs):
        super(ESConnection, self).__init__(**kwargs)
        self._set_auth_region_name(region)
        self._set_auth_service_name("es")

    def _required_auth_capability(self):
        return ['hmac-v4']

if __name__ == "__main__":
    print 'connecting to {}'.format(os.environ['ES_CLUSTER_DNS'])
    client = ESConnection(
            region=os.environ['ESTEST_REGION'],
            host=os.environ['ES_CLUSTER_DNS'],
            aws_access_key_id=os.environ['ESTEST_AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['ESTEST_AWS_SECRET_ACCESS_KEY'],
            is_secure=False)

    data='{"type": "s3","settings": { ' + \
            '"bucket": "' + os.environ['ESTEST_MANUAL_SNAPSHOT_S3_BUCKET'] + \
            '","region": "' + os.environ['ESTEST_REGION'] + \
            '","role_arn": "' + os.environ['ESTEST_IAM_MANUAL_SNAPSHOT_ROLE_ARN'] + \
            '"}}'
    print 'Registering Snapshot Repository'
    print data
    print 'waiting...'
    resp = client.make_request(method='POST',
            path='/_snapshot/backups',
            data=data)
    body = resp.read()
    print body
