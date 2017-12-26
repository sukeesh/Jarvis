from sqlobject import ForeignKey, IntCol, SQLMultipleJoin, SQLObject, \
    StringCol, func
from sqlobject.views import ViewSQLObject
from sqlobject.tests.dbtest import inserts, setupClass


class PhoneNumber(SQLObject):
    number = StringCol()
    calls = SQLMultipleJoin('PhoneCall')
    incoming = SQLMultipleJoin('PhoneCall', joinColumn='toID')


class PhoneCall(SQLObject):
    phoneNumber = ForeignKey('PhoneNumber')
    to = ForeignKey('PhoneNumber')
    minutes = IntCol()


class ViewPhoneCall(ViewSQLObject):
    class sqlmeta:
        idName = PhoneCall.q.id
        clause = PhoneCall.q.phoneNumberID == PhoneNumber.q.id

    minutes = IntCol(dbName=PhoneCall.q.minutes)
    number = StringCol(dbName=PhoneNumber.q.number)
    phoneNumber = ForeignKey('PhoneNumber', dbName=PhoneNumber.q.id)
    call = ForeignKey('PhoneCall', dbName=PhoneCall.q.id)


class ViewPhone(ViewSQLObject):
    class sqlmeta:
        idName = PhoneNumber.q.id
        clause = PhoneCall.q.phoneNumberID == PhoneNumber.q.id

    minutes = IntCol(dbName=func.SUM(PhoneCall.q.minutes))
    numberOfCalls = IntCol(dbName=func.COUNT(PhoneCall.q.phoneNumberID))
    number = StringCol(dbName=PhoneNumber.q.number)
    phoneNumber = ForeignKey('PhoneNumber', dbName=PhoneNumber.q.id)
    calls = SQLMultipleJoin('PhoneCall', joinColumn='phoneNumberID')
    vCalls = SQLMultipleJoin('ViewPhoneCall', joinColumn='phoneNumberID',
                             orderBy='id')


class ViewPhoneMore(ViewSQLObject):
    ''' View on top of view '''
    class sqlmeta:
        idName = ViewPhone.q.id
        clause = ViewPhone.q.id == PhoneCall.q.toID

    number = StringCol(dbName=ViewPhone.q.number)
    timesCalled = IntCol(dbName=func.COUNT(PhoneCall.q.toID))
    timesCalledLong = IntCol(dbName=func.COUNT(PhoneCall.q.toID))
    timesCalledLong.aggregateClause = PhoneCall.q.minutes > 10
    minutesCalled = IntCol(dbName=func.SUM(PhoneCall.q.minutes))


class ViewPhoneMore2(ViewPhoneMore):
    class sqlmeta:
        table = 'vpm'


class ViewPhoneInnerAggregate(ViewPhone):
    twiceMinutes = IntCol(dbName=func.SUM(PhoneCall.q.minutes) * 2)


def setup_module(mod):
    global calls, phones, sqlrepr
    setupClass([PhoneNumber, PhoneCall])
    ViewPhoneCall._connection = PhoneNumber._connection
    ViewPhone._connection = PhoneNumber._connection
    ViewPhoneMore._connection = PhoneNumber._connection
    phones = inserts(PhoneNumber, [('1234567890',), ('1111111111',)], 'number')
    calls = inserts(PhoneCall, [(phones[0], phones[1], 5),
                                (phones[0], phones[1], 20),
                                (phones[1], phones[0], 10),
                                (phones[1], phones[0], 25)],
                    'phoneNumber to minutes')
    sqlrepr = PhoneNumber._connection.sqlrepr


def testSimpleVPC():
    assert hasattr(ViewPhoneCall, 'minutes')
    assert hasattr(ViewPhoneCall, 'number')
    assert hasattr(ViewPhoneCall, 'phoneNumberID')


def testColumnSQLVPC():
    assert str(sqlrepr(ViewPhoneCall.q.id)) == 'view_phone_call.id'
    assert str(sqlrepr(ViewPhoneCall.q.minutes)) == 'view_phone_call.minutes'
    q = sqlrepr(ViewPhoneCall.q)
    assert q.count('phone_call.minutes AS minutes')
    assert q.count('phone_number.number AS number')


def testAliasOverride():
    assert str(sqlrepr(ViewPhoneMore2.q.id)) == 'vpm.id'


def checkAttr(cls, id, attr, value):
        assert getattr(cls.get(id), attr) == value


def testGetVPC():
    checkAttr(ViewPhoneCall, calls[0].id, 'number',
              calls[0].phoneNumber.number)
    checkAttr(ViewPhoneCall, calls[0].id, 'minutes', calls[0].minutes)
    checkAttr(ViewPhoneCall, calls[0].id, 'phoneNumber', calls[0].phoneNumber)
    checkAttr(ViewPhoneCall, calls[2].id, 'number',
              calls[2].phoneNumber.number)
    checkAttr(ViewPhoneCall, calls[2].id, 'minutes', calls[2].minutes)
    checkAttr(ViewPhoneCall, calls[2].id, 'phoneNumber', calls[2].phoneNumber)


def testGetVP():
    checkAttr(ViewPhone, phones[0].id, 'number', phones[0].number)
    checkAttr(ViewPhone, phones[0].id, 'minutes',
              phones[0].calls.sum(PhoneCall.q.minutes))
    checkAttr(ViewPhone, phones[0].id, 'phoneNumber', phones[0])


def testGetVPM():
    checkAttr(ViewPhoneMore, phones[0].id, 'number', phones[0].number)
    checkAttr(ViewPhoneMore, phones[0].id, 'minutesCalled',
              phones[0].incoming.sum(PhoneCall.q.minutes))
    checkAttr(ViewPhoneMore, phones[0].id, 'timesCalled',
              phones[0].incoming.count())
    checkAttr(ViewPhoneMore, phones[0].id, 'timesCalledLong',
              phones[0].incoming.filter(PhoneCall.q.minutes > 10).count())


def testJoinView():
    p = ViewPhone.get(phones[0].id)
    assert p.calls.count() == 2
    assert p.vCalls.count() == 2
    assert p.vCalls[0] == ViewPhoneCall.get(calls[0].id)


def testInnerAggregate():
    checkAttr(ViewPhoneInnerAggregate, phones[0].id, 'twiceMinutes',
              phones[0].calls.sum(PhoneCall.q.minutes) * 2)


def testSelect():
    s = ViewPhone.select()
    assert s.count() == len(phones)
    s = ViewPhoneCall.select()
    assert s.count() == len(calls)


def testSelect2():
    s = ViewPhone.select(ViewPhone.q.number == phones[0].number)
    assert s.getOne().phoneNumber == phones[0]


def testDistinctCount():
    # This test is for SelectResults non-* based count when distinct
    # We're really just checking this doesn't raise anything
    # due to lack of sqlrepr'ing.
    assert ViewPhone.select(distinct=True).count() == 2
