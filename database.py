import json
from collections import Counter

import pg8000 as pg
from prettytable import PrettyTable as pT


class Database:
    def __init__(
        self, user, password, host="localhost", port=5432, database=None, schema=None
    ):
        self.conn = pg.connect(
            user=user, password=password, host=host, port=port, database=database
        )
        self.c = self.conn.cursor()
        if schema is not None:
            self.c.execute("SET search_path TO {}".format(schema))

    def insert(self, table, *args, **kwargs):

        if args:
            s = "INSERT INTO {} VALUES{}".format(table, args)
            self.c.execute(s)
            self.conn.commit()
        elif kwargs:
            k = json.dumps(list(kwargs.keys()))
            v = json.dumps(list(kwargs.values())).replace('"', "'")
            s = "INSERT INTO {}({}) VALUES({})".format(
                table, k[1 : len(k) - 1], v[1 : len(v) - 1]
            )
            self.c.execute(s)
            self.conn.commit()
        else:
            raise TypeError
        return s

    def delete(self, table, **kwargs):
        if kwargs:
            s1 = ""
            for i, j in kwargs.items():
                if isinstance(j, str):
                    s1 += "{}='{}' AND ".format(i, j)
                else:
                    s1 += "{}={} AND ".format(i, j)
            s = "DELETE from {} where {}".format(table, s1[: len(s1) - 5])
            self.c.execute(s)
            self.conn.commit()
            return s
        else:
            raise TypeError

    def update(self, table, condition, **kwargs):
        if kwargs and condition:
            s1 = ""
            for i, j in kwargs.items():
                if isinstance(j, str):
                    s1 += "{} = '{}' AND ".format(i, j)
                else:
                    s1 += "{} = {} AND ".format(i, j)
            s = "UPDATE {} set {} where {}".format(table, s1[: len(s1) - 5], condition)
            self.c.execute(s)
            self.conn.commit()
            return s
        else:
            raise TypeError

    def get(
        self,
        table,
        columns="*",
        where=None,
        groupby=None,
        having=None,
        orderby=None,
        offset=None,
        limit=None,
        alias=None,
        output=True,
    ):
        s = "SELECT {} from {}".format(columns, table)
        if where:
            s += " WHERE {}".format(where)
        if groupby:
            s += " GROUP BY {}".format(groupby)
        if having:
            s += " HAVING {}".format(having)
        if orderby:
            s += " ORDER BY {}".format(orderby)
        if alias:
            s += " AS {}".format(alias)
        if offset:
            s += " OFFSET {}".format(offset)
        if limit:
            s += " LIMIT {}".format(limit)
        if output:
            self.display_query(s)
        return s

    def join(self, table1, table2, condition="", alias=None, direction="INNER"):
        if condition:
            s = "{} {} JOIN {} on {}".format(table1, direction, table2, condition)
        else:
            s = "{} NATURAL JOIN {}".format(table1, table2)
        if alias:
            s += " AS {}".format(alias)
        return s

    def union(self, table1, table2, All="", alias=None, output=True):
        s = "{} UNION {} {}".format(table1, All, table2)
        if alias:
            s += " AS {}".format(alias)
        if output:
            self.display_query(s)
        return s

    def intersection(self, table1, table2, All="", alias=None, output=True):
        s = "{} intersect {} {}".format(table1, All, table2)
        if alias:
            s += " AS {}".format(alias)
        if output:
            self.display_query(s)
        return s

    def Except(self, table1, table2, All="", alias=None, output=True):
        s = "{} except {} {}".format(table1, All, table2)
        if alias:
            s += " AS {}".format(alias)
        if output:
            self.display_query(s)
        return s

    def semi_join(self, table1, table2, alias=None, output=True):
        s = "{} IN {}".format(table1, table2)
        if alias:
            s += " AS {}".format(alias)
        if output:
            self.display_query(s)
        return s

    def semi_diff(self, table1, table2, alias=None, output=True):
        s = "{} NOT IN {}".format(table1, table2)
        if alias:
            s += " AS {}".format(alias)
        if output:
            self.display_query(s)
        return s

    def display_query(self, query, output=True):
        res = self.c.execute(query)
        self.conn.commit()
        st = Counter()
        for i, k in enumerate(self.c.description):
            temp = k[0].decode("ascii")
            if temp in st:
                temp += str(st[temp])
            st[temp] += 1

        t = pT(st)
        res = res.fetchall()
        A = []
        for i in range(len(res)):
            A.append(list(map(str, res[i])))
            t.add_row(res[i])
        if output:
            print(t)
        return A


if __name__ == "__main__":

    data = Database(
        "201701178",
        "201701178",
        "10.100.71.21",
        database="201701178",
        schema="playstore",
    )
    from pprint import pprint
    pprint(data.display_query(data.get("app"), output=False))