from __future__ import print_function, unicode_literals

import itertools
import sys

from clint.textui import colored, indent, puts
from pyfiglet import figlet_format as figlet
from PyInquirer import Separator, Token, prompt, style_from_dict

from playstore import PlayStore


def convert(val, ans):
    if "int" in val:
        return int(ans)
    elif "numeric" in val:
        return float(ans)
    elif "bool" == val:
        return True if ans == "true" else False
    else:
        return ans


db = PlayStore()

puts(colored.green(figlet("PlayStore")))

style = style_from_dict(
    {
        Token.Separator: "#15ff00",
        Token.QuestionMark: "#673ab7 bold",
        Token.Selected: "#cc5454",  # default
        Token.Pointer: "#66d9ef bold",
        Token.Instruction: "#ae81ff",  # default
        Token.Answer: "#f44336 bold",
        Token.Question: "#66d9ef",
    }
)

q1 = [
    {
        "type": "input",
        "message": "Enter your userid (email)",
        "name": "userid",
        "validate": lambda text: len(text) != 0 or "Enter a valid userid",
    },
    {
        "type": "list",
        "message": "Select option",
        "name": "product",
        "choices": [{"name": "App"}, {"name": "Book"}, {"name": "Account"}],
        "validate": lambda answer: "You must choose a product."
        if len(answer) == 0
        else True,
    },
]

a1 = prompt(q1, style=style)
if a1["product"] == "App":
    q2 = [
        {
            "type": "list",
            "message": "Select option",
            "name": "option",
            "choices": [{"name": "Install"}, {"name": "Update"}, {"name": "Uninstall"}, {"name": "Wishlist"}],
            "validate": lambda answer: "You must choose at least one option."
            if len(answer) == 0
            else True,
        }
    ]

    q3 = [
        {
            "type": "list",
            "message": "Select option",
            "name": "option",
            "choices": [
                {"name": "previously installed apps"},
                {"name": "wishlisted apps"},
                {"name": "trending apps"},
                {"name": "best rated apps"},
                {"name": "category wise apps"},
                {"name": "search apps"},
            ],
            "validate": lambda answer: "You must choose at least one option."
            if len(answer) == 0
            else True,
        }
    ]
    q4 = [
        {
            "type": "checkbox",
            "message": "Select app you want to install",
            "name": "install",
            "choices": [],
        }
    ]
    q5 = [
        {
            "type": "checkbox",
            "message": "Select category from which you want to install app",
            "name": "category",
            "choices": [],
        }
    ]
    q6 = [
        {
            "type": "confirm",
            "name": "buy",
            "message": "Do you want to buy the app?",
            "default": False,
        }
    ]
    q7 = [
        {
            "type": "list",
            "message": "Select payment method",
            "name": "payment",
            "choices": [],
            "validate": lambda answer: "You must choose at least one option."
            if len(answer) == 0
            else True,
        }
    ]
    q8 = [
        {
            "type": "list",
            "message": "Enter rating",
            "name": "rating",
            "choices": [1, 2, 3, 4, 5],
        },
        {
            "type": "input",
            "message": "Give Review",
            "name": "comment",
        }
    ]

    dcommand = {"Uninstall": False, "Update": True, "Feedback": True}

    a2 = prompt(q2, style=style)
    if a2["option"] == "Install":
        a3 = prompt(q3, style=style)

        if a3["option"] == "previously installed apps":
            apps = db.downloaded_app(a1["userid"], False, False)
            apps = dict(apps)
            if apps == {}:
                puts(
                    colored.red(
                        "You don't have any app in previously installed apps!"
                    )
                )
                
                sys.exit()
            for i in apps.keys():
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)

        elif a3["option"] == "wishlisted apps":
            apps = db.get_wishlist(a1["userid"], True, False)
            apps = dict(apps)
            if apps == {}:
                puts(
                    colored.red(
                        "You don't have any app in wishlisted apps!"
                    )
                )
                
                sys.exit()
            for i in apps.keys():
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)

        elif a3["option"] == "trending apps":
            apps = db.trending(True, False)
            apps = dict(apps)
            for i in apps.keys():
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)

        elif a3["option"] == "best rated apps":
            apps = db.best_rated(True, False)
            apps = dict(apps)
            for i in apps.keys():
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)

        elif a3["option"] == "category wise apps":
            cats = db.get_category()
            for i in itertools.chain.from_iterable(cats):
                q5[0]["choices"].append({"name": i})
            a5 = prompt(q5, style=style)
            for i in a5["category"]:
                apps = db.category_wise(i, False)
                apps = dict(apps)
            for i in apps.keys():
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)

        else:
            q9 = [
                {
                    "type": "input",
                    "message": "Enter name of the app",
                    "name": "search",
                    "validate": lambda text: len(text) != 0 or "Field can't be empty.",
                }
            ]
        
            a9 = prompt(q9, style=style)
            s = db.get("app", "appname, appid", where="name='{}'".format(a9["search"]), output=False)
            apps = db.display_query(s, output=False)
            if apps == []:
                puts(
                    colored.red(
                        "{} does not exist in database.".format(a9["search"])
                    )
                )
            else:
                apps = dict(apps)
                for i in apps.keys():
                    q4[0]["choices"].append({"name": i})
                a4 = prompt(q4, style=style)

        if a4["install"] == []:
            puts(colored.red("You have to select at least one app."))
        else:
            for i in a4["install"]:
                s = db.download(a1["userid"], apps[i])
                if not s:
                    puts(
                        colored.red(
                            "{} is a paid app, you have to pay to download it".format(i)
                        )
                    )
                    a6 = prompt(q6, style=style)
                    pays = {}
                    if a6["buy"]:
                        for j in ("debitcard", "creditcard", "ewallet", "netbanking"):
                            q7[0]["choices"].append(Separator("= {} =".format(j)))
                            payments = db.get_payment(a1["userid"], j, False)
                            payments = dict(payments)
                            for k in payments.keys():
                                q7[0]["choices"].append({"name": k})
                            pays.update(dict(payments))
                        a7 = prompt(q7, style=style)
                        s = db.download(a1["userid"], apps[i], pays.get(a7["payment"]))
                        if s:
                            puts(colored.green("{} downloaded successfully.".format(i)))
                        else:
                            puts(colored.red("download of {} failed. may be because your card has been expired".format(i)))
                else:
                    puts(colored.green("{} downloaded successfully.".format(i)))

    elif a2["option"] in dcommand:
        apps = db.downloaded_app(a1["userid"], True, False)
        apps = dict(apps)
        for i in apps.keys():
            q4[0]["choices"].append({"name": i})
        q4[0]["message"] = "Select app you want to {}".format(a2["option"])
        a4 = prompt(q4, style=style)
        if a4["install"] == []:
            puts(colored.red("You have to select at least one app."))
        elif a2["option"] == "Feedback":
            for i in a4["install"]:
                puts(colored.green(i))  
                a8 = prompt(q8, style=style)
                db.feedback(a1["userid"], apps[i], a8["rating"], a8["comment"])
        else:
            for i in a4["install"]:
                s = db.download(a1["userid"], apps[i], install=dcommand[a2["option"]])
                puts(colored.green("{} {}ed successfully.".format(i, a2["option"])))
    
    elif a2["option"] == "Wishlist":
        q3 = [
            {
                "type": "list",
                "message": "Select option",
                "name": "option",
                "choices": [
                    {"name": "remove wishlisted apps"},
                    {"name": "trending apps"},
                    {"name": "best rated apps"},
                    {"name": "category wise apps"},
                    {"name": "search apps"}
                ],
                "validate": lambda answer: "You must choose at least one option."
                if len(answer) == 0
                else True,
            }
        ]
        q4 = [
            {
                "type": "checkbox",
                "message": "Select app you want to add to/(remove from) wishlist ",
                "name": "install",
                "choices": [],
            }
        ]
        a3 = prompt(q3, style=style)
        if a3["option"] == "remove wishlisted apps":
            apps = db.get_wishlist(a1["userid"], True, False)
            if apps == []:
                puts(colored.red("Your wishlist is empty!"))
                
                sys.exit()
            apps = dict(apps)
            for i in apps.keys():
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)

        elif a3["option"] == "trending apps":
            apps = db.trending(True, False)
            apps = dict(apps)
            for i in apps.keys():
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)

        elif a3["option"] == "best rated apps":
            apps = db.best_rated(True, False)
            apps = dict(apps)
            for i in apps.keys():
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)

        elif a3["option"] == "category wise apps":
            cats = db.get_category()
            for i in itertools.chain.from_iterable(cats):
                q5[0]["choices"].append({"name": i})
            a5 = prompt(q5, style=style)
            for i in a5["category"]:
                apps = db.category_wise(i, False)
                apps = dict(apps)
            for i in apps.keys():
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)
        else:
            q9 = [
                {
                    "type": "input",
                    "message": "Enter name of the app",
                    "name": "search",
                    "validate": lambda text: len(text) != 0 or "Field can't be empty.",
                }
            ]
        
            a9 = prompt(q9, style=style)
            s = db.get("app", "appname, appid", where="name='{}'".format(a9["search"]), output=False)
            apps = db.display_query(s, output=False)
            if apps == []:
                puts(
                    colored.red(
                        "{} does not exist in database.".format(a9["search"])
                    )
                )
            else:
                apps = dict(apps)
                for i in apps.keys():
                    q4[0]["choices"].append({"name": i})
                a4 = prompt(q4, style=style)

        if a4["install"] == []:
            puts(colored.red("You have to select at least one app."))
        elif a3["option"] == "remove wishlisted apps":
            for i in a4["install"]:
                db.remove_wishlist(a1["userid"], apps[i])
                puts(colored.green("{} removed from wishlist successfully.".format(i)))
        else:
            for i in a4["install"]:
                s = db.wishlist(a1["userid"], apps[i])
                if not s:
                    puts(colored.red("App can't be added to wishlist because app is already downloaded/wishlisted."))
                else:
                    puts(colored.green("{} added to wishlist successfully.".format(i)))


elif a1["product"] == "Book":
    q2 = [
        {
            "type": "list",
            "message": "Select category from which you want to show/purchase book.",
            "name": "option",
            "choices": [
                {"name": "wishlisted books"},
                {"name": "best rated books"},
                {"name": "genre wise books"},
                {"name": "my library"},
                {"name": "search books"},
                {"name": "wishlist books"},
            ],
            "validate": lambda answer: "You must choose at least one option."
            if len(answer) == 0
            else True,
        }
    ]
    q3 = [
        {
            "type": "checkbox",
            "message": "Select book you want to purchase",
            "name": "purchase",
            "choices": [],
        }
    ]
    q4 = [
        {
            "type": "checkbox",
            "message": "Select genre from which you want to purchase book",
            "name": "genre",
            "choices": [],
        }
    ]
    q6 = [
        {
            "type": "confirm",
            "name": "buy",
            "message": "Do you want to buy the app?",
            "default": False,
        }
    ]
    q7 = [
        {
            "type": "list",
            "message": "Select payment method",
            "name": "payment",
            "choices": [],
            "validate": lambda answer: "You must choose at least one option."
            if len(answer) == 0
            else True,
        }
    ]
    q8 = [
        {
            "type": "list",
            "message": "Enter rating",
            "name": "rating",
            "choices": ['1', '2', '3', '4', '5'],
        },
        {
            "type": "input",
            "message": "Give Review",
            "name": "comment",
        }
    ]
    a2 = prompt(q2, style=style)

    if a2["option"] == "wishlisted books":
        books = db.get_wishlist(a1["userid"], False, False)
        books = dict(books)
        if books == {}:
            puts(
                colored.red(
                    "You don't have any book in wishlisted books!"
                )
            )
            
            sys.exit()
        for i in books.keys():
            q3[0]["choices"].append({"name": i})
        a3 = prompt(q3, style=style)


    elif a2["option"] == "best rated books":
        books = db.best_rated(False, False)
        books = dict(books)
        for i in books.keys():
            q3[0]["choices"].append({"name": i})
        a3 = prompt(q3, style=style)

    elif a2["option"] == "genre wise books":
        cats = db.get_genre()
        for i in itertools.chain.from_iterable(cats):
            q4[0]["choices"].append({"name": i})
        a4 = prompt(q4, style=style)
        for i in a4["genre"]:
            books = db.genre_wise(i, False)
            books = dict(books)
        for i in books.keys():
            q3[0]["choices"].append({"name": i})
        a3 = prompt(q3, style=style)

    elif a2["option"] == "my library":
        books = db.downloaded_book(a1["userid"], False)
        books = dict(books)
        if books == {}:
            puts(
                colored.red(
                    "You don't have any books in your library!"
                )
            )
            
            sys.exit()
        q3[0]["message"] = "Select books if you want to give feedback"
        for i in books.keys():
            q3[0]["choices"].append({"name": i})
        a3 = prompt(q3, style=style)
        if a3["purchase"] != []:
            for i in a3["purchase"]:
                puts(colored.green(i))  
                a8 = prompt(q8, style=style)
                s = db.feedback(a1["userid"], books[i], a8["rating"], a8["comment"])
                print(s)
        
        sys.exit()
    
    elif a2["option"] == "search books":
        q9 = [
            {
                "type": "input",
                "message": "Enter name of the book",
                "name": "search",
                "validate": lambda text: len(text) != 0 or "Field can't be empty.",
            }
        ]
        
        a9 = prompt(q9, style=style)
        s = db.get("book", "name, isbn", where="name='{}'".format(a9["search"]), output=False)
        books = db.display_query(s, output=False)
        if books == []:
            puts(
                colored.red(
                    "{} does not exist in database.".format(a9["search"])
                )
            )
        else:
            books = dict(books)
            for i in books.keys():
                q3[0]["choices"].append({"name": i})
            a3 = prompt(q3, style=style)
            
    
    else:
        q2 = [
            {
                "type": "list",
                "message": "Select category from which you want to wishlist/unwishlist book.",
                "name": "option",
                "choices": [
                    {"name": "remove wishlisted books"},
                    {"name": "best rated books"},
                    {"name": "genre wise books"},
                    {"name": "search books"}
                ],
                "validate": lambda answer: "You must choose at least one option."
                if len(answer) == 0
                else True,
            }
        ]
        q4 = [
            {
                "type": "checkbox",
                "message": "Select book you want to add to wishlist",
                "name": "purchase",
                "choices": [],
            }
        ]
        q3 = [
            {
                "type": "checkbox",
                "message": "Select genre from which you want to add book to your wishlist",
                "name": "category",
                "choices": [],
            }
        ]
        a2 = prompt(q2, style=style)

        if a2["option"] == "remove wishlisted books":
            books = db.get_wishlist(a1["userid"], False, False)
            books = dict(books)
            if books == {}:
                puts(
                    colored.red(
                        "You don't have any book in wishlisted books!"
                    )
                )
                
                sys.exit()
            for i in books.keys():
                q3[0]["choices"].append({"name": i})
            a3 = prompt(q3, style=style)

        elif a2["option"] == "best rated books":
            books = db.best_rated(False, False)
            books = dict(books)
            for i in books.keys():
                q3[0]["choices"].append({"name": i})
            a3 = prompt(q3, style=style)

        elif a2["option"] == "genre wise books":
            cats = db.get_genre()
            for i in itertools.chain.from_iterable(cats):
                q4[0]["choices"].append({"name": i})
            a4 = prompt(q4, style=style)
            for i in a4["genre"]:
                books = db.genre_wise(i, False)
                books = dict(books)
            for i in books.keys():
                q3[0]["choices"].append({"name": i})
            a3 = prompt(q3, style=style)
        else:
            q9 = [
                {
                    "type": "input",
                    "message": "Enter name of the book",
                    "name": "search",
                    "validate": lambda text: len(text) != 0 or "Field can't be empty.",
                }
            ]
        
            a9 = prompt(q9, style=style)
            s = db.get("book", "name, isbn", where="name='{}'".format(a9["search"]), output=False)
            books = db.display_query(s, output=False)
            if books == []:
                puts(
                    colored.red(
                        "{} does not exist in database.".format(a9["search"])
                    )
                )
            else:
                books = dict(books)
                for i in books.keys():
                    q3[0]["choices"].append({"name": i})
                a3 = prompt(q3, style=style)
        if a3["purchase"] == []:
            puts(colored.red("You have to select at least one book."))
        else:
            for i in a3["purchase"]:
                s = db.wishlist(a1["userid"], books[i], False)
                if not s:
                    puts(colored.red("Book can't be added to wishlist because book is already downloaded/wishlisted."))
                else:
                    puts(colored.green("{} added to wishlist successfully.".format(i)))
        
        sys.exit()
        

    if a3["purchase"] == []:
        puts(colored.red("You have to select at least one book."))
    else:
        for i in a3["purchase"]:
            s = db.download(a1["userid"], books[i], isApp=False)
            if not s:
                puts(
                    colored.red(
                        "{} is a paid book, you have to pay to download it".format(i)
                    )
                )
                a6 = prompt(q6, style=style)
                pays = {}
                if a6["buy"]:
                    for j in ("debitcard", "creditcard", "ewallet", "netbanking"):
                        q7[0]["choices"].append(Separator("= {} =".format(j)))
                        payments = db.get_payment(a1["userid"], j, False)
                        payments = dict(payments)
                        for k in payments.keys():
                            q7[0]["choices"].append({"name": k})
                        pays.update(dict(payments))
                    a7 = prompt(q7, style=style)
                    s = db.download(a1["userid"], books[i], pays.get(a7["payment"]), isApp=False)
                    print(s)
                    if s:
                        puts(colored.green("{} added to your library successfully.".format(i)))
            else:
                puts(colored.green("{} added to your library successfully.".format(i)))

elif a1["product"] == "Account":
    q2 = [
        {
            "type": "list",
            "message": "Select option",
            "name": "option",
            "choices": ["add payment method", "edit user details", "delete account"],
        }
    ]
    q3 = [
        {
            "type": "list",
            "message": "Select payment method you want to add",
            "name": "option",
            "choices": ["credit card", "debit card", "ewallet", "netbanking"],   
        }
    ]
    q4 = [
        {
            "type": "checkbox",
            "message": "Select fields you want to update",
            "name": "option",
            "choices": ["userid", "username", "country", "autoupdate"]  
        }
    ]

    q6 = [
        {
            "type": "confirm",
            "message": "Are you sure you want to delete your account.",
            "name": "option",
        }
    ]

    a2 = prompt(q2, style=style)
    
    if a2["option"] == "add payment method":
        a3 = prompt(q3, style=style)
        d = {}
        if a3["option"] in {"credit card", "debit card"}:
            for i in ("name", "expdate", "cardno"):
                q5 = [
                    {
                        "type": "input",
                        "message": "Enter {}",
                        "name": "option",
                        "validate": lambda text: len(text) != 0 or "Field can't be empty.",
                        
                    }
                ]
                q5[0]["message"] = q5[0]["message"].format(i)
                a5 = prompt(q5, style=style)
                d.update(i=a5["option"])
            db.add_card(d["name"], a1["userid"], d["expdate"], d["cardno"], "".join(a3["option"].split()))
        elif a3["option"] == "ewallet":
            for i in ("name", "walletid"):
                q5 = [
                    {
                        "type": "input",
                        "message": "Enter {}",
                        "name": "option",
                        "validate": lambda text: len(text) != 0 or "Field can't be empty.",
                        
                    }
                ]
                q5[0]["message"] = q5[0]["message"].format(i)
                a5 = prompt(q5, style=style)
                d.update(i=a5["option"])
            db.add_wallet(a1["userid"], d["name"], d["walletid"])
        else:
            q5 = [
                {
                    "type": "input",
                    "message": "Enter {}",
                    "name": "option",
                    "validate": lambda text: len(text) != 0 or "Field can't be empty.",
                    
                }
            ]
            q5[0]["message"] = q5[0]["message"].format("bank name")
            a5 = prompt(q5, style=style)
            db.add_netbank(a1["userid"], a5["option"])
        
    elif a2["option"] == "edit user details":
        a4 = prompt(q4, style=style)
        if a4["option"] != []:
            ans = []
            for i in a4["option"]:
                q5 = [
                    {
                        "type": "input",
                        "message": "Enter {}",
                        "name": "option",
                        "validate": lambda text: len(text) != 0 or "Field can't be empty.",
                        
                    }
                ]
                q5[0]["message"] = q5[0]["message"].format(i)
                a5 = prompt(q5, style=style)
                ans.append(a5["option"])
            kwargs = dict([a4["option"], ans])
            db.update("users", "userid='{}'".format(a1["userid"]), **kwargs)
    else:
        a6 = prompt(q6, style=style)
        if a6["option"]:
            db.delete("users", userid=a1["userid"])

