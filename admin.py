from __future__ import print_function, unicode_literals

import json

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
tables = sorted(db.schema_struct.keys())

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
        "type": "list",
        "message": "Select command",
        "name": "command",
        "choices": [
            {"name": "Insert"},
            {"name": "Update"},
            {"name": "Delete"},
            {"name": "Get"},
            {"name": "Query"},
            {"name": "Interactive"},
        ],
        "validate": lambda answer: "You must choose at least one command."
        if len(answer) == 0
        else True,
    }
]
q2 = [
    {
        "type": "list",
        "message": "Select Table",
        "name": "table",
        "choices": tables,
        "validate": lambda answer: "You must choose at least one table."
        if len(answer) == 0
        else True,
    }
]

a1 = prompt(q1, style=style)
if a1["command"] in {"Insert", "Get", "Update", "Delete"}:
    a2 = prompt(q2, style=style)
    if a1["command"] == "Insert":
        q3 = []
        attrs = db.schema_struct[a2["table"]]
        for attr in attrs:
            q3.append(
                {
                    "type": "input",
                    "message": "Enter {} ({})".format(attr, attrs[attr]["type"]),
                    "name": attr,
                }
            )
        a3 = prompt(q3, style=style)
        try:
            for i, j in a3.items():
                a3[i] = convert(attrs[i]["type"], j)
            s = db.insert(a2["table"], **a3)
            puts(colored.green('Query "{}" executed successfully'.format(s)))
        except Exception as e:
            puts(colored.red(e))

    elif a1["command"] == "Delete":
        choices = [Separator("= {} =".format(a2["table"]))]
        attrs = db.schema_struct[a2["table"]]
        for i in attrs:
            choices.append({"name": i})
        q4 = [
            {
                "type": "checkbox",
                "message": "Select attributes for compare condition",
                "name": "delattr",
                "choices": choices,
            }
        ]
        a4 = prompt(q4, style=style)
        q5 = []
        for attr in a4["delattr"]:
            q5.append(
                {
                    "type": "input",
                    "message": "Enter {} ({})".format(attr, attrs[attr]["type"]),
                    "name": attr,
                }
            )
        a5 = prompt(q5, style=style)

        try:
            for i, j in a5.items():
                a5[i] = convert(attrs[i]["type"], j)
            s = db.delete(a2["table"], **a5)
            puts(colored.green('Query "{}" executed successfully'.format(s)))
        except Exception as e:
            puts(colored.red(e))

    elif a1["command"] == "Update":
        choices = [Separator("= {} =".format(a2["table"]))]
        attrs = db.schema_struct[a2["table"]]
        for i in attrs:
            choices.append({"name": i})
        q4 = [
            {
                "type": "checkbox",
                "message": "Select attributes for compare condition",
                "name": "upattr",
                "choices": choices,
            }
        ]
        a4 = prompt(q4, style=style)
        q5 = []
        for attr in a4["upattr"]:
            q5.append(
                {
                    "type": "input",
                    "message": "Enter {} ({})".format(attr, attrs[attr]["type"]),
                    "name": attr,
                }
            )
        a5 = prompt(q5, style=style)
        s1 = ""
        try:
            for i, j in a5.items():
                a5[i] = convert(attrs[i]["type"], j)
        except Exception as e:
            puts(colored.red(e))

        for i, j in a5.items():
            if isinstance(j, str):
                s1 += "{}='{}' AND ".format(i, j)
            else:
                s1 += "{}={} AND ".format(i, j)
        s1 = s1[: len(s1) - 5]
        q6 = [
            {
                "type": "checkbox",
                "message": "Select attributes you want to update",
                "name": "setattr",
                "choices": choices,
            }
        ]

        a6 = prompt(q6, style=style)
        q7 = []
        for attr in a6["setattr"]:
            q7.append(
                {
                    "type": "input",
                    "message": "Enter {} ({})".format(attr, attrs[attr]["type"]),
                    "name": attr,
                }
            )
        a7 = prompt(q7, style=style)

        try:
            for i, j in a7.items():
                a7[i] = convert(attrs[i]["type"], j)
            s = db.update(a2["table"], s1, **a7)
            puts(colored.green('Query "{}" executed successfully'.format(s)))
        except Exception as e:
            puts(colored.red(e))

    elif a1["command"] == "Get":
        choices = [Separator("= {} =".format(a2["table"]))]
        attrs = db.schema_struct[a2["table"]]
        for i in attrs:
            choices.append({"name": i})
        q4 = [
            {
                "type": "checkbox",
                "message": "Select attributes you want to display",
                "name": "getattr",
                "choices": choices,
            }
        ]
        a4 = prompt(q4, style=style)
        try:
            columns = json.dumps(a4["getattr"])
            s = db.get(a2["table"], columns=columns[1 : len(columns) - 1])
            puts(colored.green('Query "{}" executed successfully'.format(s)))
        except Exception as e:
            puts(colored.red(e))


if a1["command"] in {"Query", "Interactive"}:
    if a1["command"] == "Interactive":
        q5 = [
            {
                "type": "input",
                "name": "function",
                "message": "Write Any valid python Database function",
                "validate": lambda text: len(text) != 0 or "Enter a valid function",
            }
        ]
        a5 = prompt(q5, style=style)
        try:
            eval(a5["function"])
        except Exception as e:
            puts(colored.red(e))

    elif a1["command"] == "Query":
        q4 = [
            {
                "type": "confirm",
                "name": "display",
                "message": "Do you want to display output table of the query?",
                "default": False,
            }
        ]
        a4 = prompt(q4, style=style)
        q5 = [
            {
                "type": "input",
                "name": "query",
                "message": "Write Any valid SQL query",
                "validate": lambda text: len(text) != 0 or "Enter a valid SQL query",
            }
        ]
        a5 = prompt(q5, style=style)
        try:
            s = db.display_query(a5["query"], a4["display"])
            puts(colored.green('Query "{}" executed successfully'.format(s)))
        except Exception as e:
            puts(colored.red(e))
