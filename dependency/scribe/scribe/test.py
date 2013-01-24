import sys
import pprint
from urlparse import urlparse
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.protocol import TBinaryProtocol

import scribe
from ttypes import *


socket = TSocket.TSocket("172.100.101.14", 1463)
transport = TTransport.TFramedTransport(socket)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = scribe.Client(protocol)
transport.open()


pprint.pprint(client.Log([LogEntry("differentone", "sameone")]))
