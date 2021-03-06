#!/usr/bin/python
from telephus.protocol import ManagedCassandraClientFactory
from telephus.client import CassandraClient
from telephus.cassandra.ttypes import ColumnPath, ColumnParent, Column, SuperColumn
from twisted.internet import defer

HOST = 'localhost'
PORT = 9160
KEYSPACE = 'Keyspace1'
CF = 'Standard1'
SCF = 'Super1'
colname = 'foo'
scname = 'bar'

@defer.inlineCallbacks
def dostuff(client):
    yield client.insert(key='test', column_family=CF, value='testval', column=colname)
    yield client.insert(key='test', column_family=SCF, value='testval', column=colname, super_column=scname)
    res = yield client.get(key='test', column_family=CF, column=colname)
    print 'get', res
    res = yield client.get(key='test', column_family=SCF, column=colname, super_column=scname)
    print 'get (super)', res
    res = yield client.get_slice(key='test', column_family=CF)
    print 'get_slice', res
    res = yield client.multiget(keys=['test', 'test2'], column_family=CF, column=colname)
    print 'multiget', res
    res = yield client.multiget_slice(keys=['test', 'test2'], column_family=CF)
    print 'multiget_slice', res
    res = yield client.get_count(key='test', column_family=CF)
    print 'get_count', res
    # batch insert will figure out if you're trying a CF or SCF
    # from the data structure
    res = yield client.batch_insert(key='test', column_family=CF, mapping={colname: 'bar'})
    print "batch_insert", res
    res = yield client.batch_insert(key='test', column_family=SCF, mapping={'foo': {colname: 'bar'}})
    print "batch_insert", res
    # with ttypes, you pass a list as you would for raw thrift
    # this way you can set custom timestamps
    cols = [Column(colname, 'bar', 1234), Column('bar', 'baz', 54321)]
    res = yield client.batch_insert(key='test', column_family=CF, mapping=cols)
    print "batch_insert", res
    cols = [SuperColumn(name=colname, columns=cols)]
    # of course you don't have to use kwargs if the order is correct
    res = yield client.batch_insert('test', SCF, cols)
    print "batch_insert", res



if __name__ == '__main__':
    from twisted.internet import reactor
    from twisted.python import log
    import sys
    log.startLogging(sys.stdout)

    f = ManagedCassandraClientFactory(KEYSPACE)
    c = CassandraClient(f)
    dostuff(c)
    reactor.connectTCP(HOST, PORT, f)
    reactor.run()
