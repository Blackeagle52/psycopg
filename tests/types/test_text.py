import pytest

import psycopg3
from psycopg3.adapt import Format


#
# tests with text
#


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
def test_adapt_1char(conn, format):
    cur = conn.cursor()
    ph = "%s" if format == Format.TEXT else "%b"
    for i in range(1, 256):
        cur.execute("select %s = chr(%%s::int)" % ph, (chr(i), i))
        assert cur.fetchone()[0], chr(i)


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
def test_cast_1char(conn, format):
    cur = conn.cursor(binary=format == Format.BINARY)
    for i in range(1, 256):
        cur.execute("select chr(%s::int)", (i,))
        assert cur.fetchone()[0] == chr(i)

    assert cur.pgresult.fformat(0) == format


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
@pytest.mark.parametrize("encoding", ["utf8", "latin9"])
def test_adapt_enc(conn, format, encoding):
    eur = "\u20ac"
    cur = conn.cursor()
    ph = "%s" if format == Format.TEXT else "%b"

    conn.encoding = encoding
    (res,) = cur.execute("select %s::bytea" % ph, (eur,)).fetchone()
    assert res == eur.encode("utf8")


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
def test_adapt_ascii(conn, format):
    eur = "\u20ac"
    cur = conn.cursor(binary=format == Format.BINARY)
    ph = "%s" if format == Format.TEXT else "%b"

    conn.encoding = "sql_ascii"
    (res,) = cur.execute("select ascii(%s)" % ph, (eur,)).fetchone()
    assert res == ord(eur)


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
def test_adapt_badenc(conn, format):
    eur = "\u20ac"
    cur = conn.cursor()
    ph = "%s" if format == Format.TEXT else "%b"

    conn.encoding = "latin1"
    with pytest.raises(UnicodeEncodeError):
        cur.execute("select %s::bytea" % ph, (eur,))


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
@pytest.mark.parametrize("encoding", ["utf8", "latin9"])
def test_cast_enc(conn, format, encoding):
    eur = "\u20ac"
    cur = conn.cursor(binary=format == Format.BINARY)

    conn.encoding = encoding
    (res,) = cur.execute("select chr(%s::int)", (ord(eur),)).fetchone()
    assert res == eur


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
def test_cast_badenc(conn, format):
    eur = "\u20ac"
    cur = conn.cursor(binary=format == Format.BINARY)

    conn.encoding = "latin1"
    with pytest.raises(psycopg3.DatabaseError):
        cur.execute("select chr(%s::int)", (ord(eur),))


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
def test_cast_ascii(conn, format):
    eur = "\u20ac"
    cur = conn.cursor(binary=format == Format.BINARY)

    conn.encoding = "sql_ascii"
    (res,) = cur.execute("select chr(%s::int)", (ord(eur),)).fetchone()
    assert res == eur.encode("utf8")


#
# tests with bytea
#


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
def test_adapt_1byte(conn, format):
    cur = conn.cursor()
    ph = "%s" if format == Format.TEXT else "%b"
    "select %s = %%s::bytea" % ph
    for i in range(0, 256):
        cur.execute("select %s = %%s::bytea" % ph, (bytes([i]), fr"\x{i:02x}"))
        assert cur.fetchone()[0], i


@pytest.mark.parametrize("format", [Format.TEXT, Format.BINARY])
def test_cast_1byte(conn, format):
    cur = conn.cursor(binary=format == Format.BINARY)
    for i in range(0, 256):
        cur.execute("select %s::bytea", (fr"\x{i:02x}",))
        assert cur.fetchone()[0] == bytes([i])

    assert cur.pgresult.fformat(0) == format
