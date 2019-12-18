from database import Database
import json


class PlayStore(Database):
    def __init__(
        self,
        user="201701178",
        password="201701178",
        host="10.100.71.21",
        port=5432,
        database="201701178",
        schema="playstore",
    ):
        super(PlayStore, self).__init__(user, password, host, port, database, schema)
        self.schema_struct = {}
        s = self.c.execute(
            "select tablename from pg_tables where schemaname='playstore'"
        )
        for i in s.fetchall():
            rows = self.c.execute(
                "SELECT COLUMN_NAME, udt_name, column_default FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'{}'".format(
                    i[0]
                )
            )
            temp = {}
            for j in rows.fetchall():
                temp[j[0]] = {"type": j[1], "default": bool(j[2])}
                self.schema_struct[i[0]] = temp

    def download(self, userid, productid, paymentid=-1, install=True, isApp=True):
        f = lambda install: "true" if install else "false"
        if isApp:
            self.c.execute(
                "SELECT set_download_app('{}', {}, {}, {})".format(
                    userid, productid, paymentid, f(install)
                )
            )
            return self.c.fetchone()[0]
        else:
            self.c.execute(
                "SELECT set_library('{}', '{}', {})".format(
                    productid, userid, paymentid
                )
            )
            return self.c.fetchone()[0]

    def wishlist(self, userid, productid, isApp=True):
        if isApp:
            self.c.execute(
                "SELECT set_wishlist_app('{}', {})".format(userid, productid)
            )
            return self.c.fetchone()[0]
        else:
            self.c.execute(
                "SELECT set_wishlist_book('{}', '{}')".format(userid, productid)
            )
            return self.c.fetchone()[0]

    def remove_wishlist(self, userid, productid, isApp=True):
        if isApp:
            self.delete("wishlistapp", userid=userid, appid=productid)
        else:
            self.delete("wishlistbook", userid=userid, bookid=productid)

    def feedback(self, userid, productid, rating, comment, isApp=True):
        if isApp:
            self.c.execute(
                "SELECT set_feedback_app({}, {}, '{}', '{}')".format(
                    rating, productid, userid, comment
                )
            )
            return self.c.fetchone()[0]
        else:
            self.c.execute(
                "SELECT set_feedback_book({}, '{}', '{}', '{}')".format(
                    rating, userid, productid, comment
                )
            )
            return self.c.fetchone()[0]

    def add_card(self, name, userid, expdate, cardno, type):
        if type == "debit":
            self.c.execute(
                "SELECT set_debit('{}', '{}', '{}', {})".format(
                    name, userid, expdate, cardno
                )
            )
        elif type == "credit":
            self.c.execute(
                "SELECT set_credit('{}', '{}', '{}', {})".format(
                    name, userid, expdate, cardno
                )
            )
        else:
            raise TypeError("Error: got invalid type value '{}'".format(type))

    def add_netbank(self, userid, bank):
        self.c.execute("SELECT set_netbanking('{}', '{}').format(userid, bank)")

    def add_wallet(self, userid, wallet_name, walletid):
        self.c.execute(
            "SELECT set_wallet('{}', '{}', '{}').format(userid, wallet_name, walletid)"
        )

    def print_schema(self):
        for i, j in self.schema_struct.items():
            print(i)
            for k in j:
                print("\t" + str(k))

    def get_comments(self, productid, isApp):
        isApp = json.dumps(isApp)
        self.display_query(
            "SELECT sort_reviews({}, {})".format(productid, isApp[1 : len(isApp) - 1])
        )

    def get_category(self):
        return self.display_query(
            self.get("category", columns="name", output=False), False
        )

    def category_wise(self, category, output):
        return self.display_query(
            self.get(
                self.join(self.join("category", "apphascategory"), "app"),
                columns="appname, appid",
                where="name='{}'".format(category),
                output=output,
            ),
            output=output,
        )

    def get_genre(self):
        return self.display_query(
            self.get("genres", columns="distinct genres", output=False), False
        )

    def genre_wise(self, genre, output):
        return self.display_query(
            self.get(
                self.join("genres", "book"),
                columns="name, isbn",
                where="genres='{}'".format(genre),
                output=output,
            ),
            output=output,
        )

    def downloaded_app(self, userid, installed, output):
        if installed:
            installed = "true"
            s = self.get(
                self.join("downloadapp", "app"),
                columns="appname, appid",
                where="userid='{}' and installed='{}'".format(userid, installed),
                output=output,
            )
            if not output:
                return self.display_query(s, output=output)
        else:
            installed = "false"
            s = self.get(
                self.join("downloadapp", "app"),
                columns="appname, appid",
                where="userid='{}' and installed='{}'".format(userid, installed),
                output=output,
            )
            if not output:
                return self.display_query(s, output=output)

    def get_wishlist(self, userid, isApp, output):
        if isApp:
            s = self.get(
                self.join("wishlistapp", "app"),
                columns="appname, appid",
                where="userid='{}'".format(userid),
                output=output,
            )
            if not output:
                return self.display_query(s, output=output)
        else:
            s = self.get(
                self.join("wishlistbook", "book"),
                columns="name, isbn",
                where="userid='{}'".format(userid),
                output=output,
            )
            if not output:
                return self.display_query(s, output=output)

    def downloaded_book(self, userid, output):
        s = self.get(
            self.join("downloadbook", "book"),
            columns="name, isbn",
            where="userid='{}'".format(userid),
            output=output,
        )
        if not output:
            return self.display_query(s, output=output)

    def trending(self, isApp, output):
        s = self.get(
            "most_downloaded_app", columns="appname, appid", limit=10, output=output
        )
        if not output:
            return self.display_query(s, output=output)

    def best_rated(self, isApp, output):
        if isApp:
            s = self.get(
                "best_rated_app", columns="appname, appid", limit=10, output=output
            )
            if not output:
                return self.display_query(s, output=output)
        else:
            s = self.get(
                "best_rated_book", columns="name, isbn", limit=10, output=output
            )
            if not output:
                return self.display_query(s, output=output)

    def get_payment(self, userid, method, output):
        d = {
            "debitcard": "cardno",
            "creditcard": "cardno",
            "ewallet": "walletid",
            "netbanking": "bankname",
        }
        s = self.get(
            self.join("payment", method),
            where="userid='{}'".format(userid),
            columns="{}, paymentid".format(d[method]),
            output=output,
        )
        if not output:
            return self.display_query(s, output=output)


if __name__ == "__main__":

    play = PlayStore()
    s = play.get_wishlist("Isai@jennifer.net", True, output=False)
    print(s)

