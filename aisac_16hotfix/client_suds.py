import base64
import hashlib
import http
import logging
import socket
import traceback
import urllib

from suds.cache import NoCache
from suds.client import Client
from suds.transport.http import HttpTransport


class HTTPSClientAuthHandler(urllib.request.HTTPSHandler):
    def __init__(self, key, cert, *args, **kwargs):
        super(HTTPSClientAuthHandler, self).__init__(*args, **kwargs)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return http.client.HTTPSConnection(
            host,
            key_file=self.key,
            cert_file=self.cert,
        )


class HTTPSClientCertTransport(HttpTransport):
    def __init__(self, key, cert, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)
        self.key = key
        self.cert = cert

    def u2open(self, u2request):
        tm = self.options.timeout
        url = urllib.request.build_opener(
            HTTPSClientAuthHandler(self.key, self.cert),
        )
        if self.u2ver() < 2.6:
            socket.setdefaulttimeout(tm)
            return url.open(u2request)
        else:
            return url.open(u2request, timeout=tm)


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        d.update(f.read())
    return d.hexdigest()


def send(
        intelligenceTypeId, iodefTypeId, filepath,
        account, pwd,
        url, cert_path, key_path,
        toUnitIds=2,
):
    try:
        client = Client(
            url=url,
            cache=NoCache(),
            transport=HTTPSClientCertTransport(
                cert=cert_path,
                key=key_path,
            ),
        )
    except:
        logging.error('Exception when connecting to server.')
        logging.error(traceback.format_exc())
        raise

    try:
        with open(filepath, 'rb') as f:
            doc = base64.b64encode(f.read()).decode()
    except:
        logging.error('Exception when reading iodef.')

    try:
        checksum = md5sum(filepath)
    except:
        logging.error('Exception when calculating md5sum.')
        raise

    try:
        response = client.service.uploadIodefFile(
            account=account,
            pwd=pwd,
            toUnitIds=toUnitIds,
            intelligenceTypeId=intelligenceTypeId,
            iodefTypeId=iodefTypeId,
            doc=doc,
            checksum=checksum,
        )
    except:
        logging.error('Exception when sending to server.')
        logging.error(traceback.format_exc())
        raise

    return response
