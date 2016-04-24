# This program tries to parse distrowatch and create a svg graph simliar to: <https://en.wikipedia.org/wiki/Linux_distribution#/media/File:Linux_Distribution_Timeline_with_Android.svg>
# Copyright (C) 2016 Jappe Klooster

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.If not, see <http://www.gnu.org/licenses/>.



import argparse
parser = argparse.ArgumentParser(
    description=
        "Distrograph Copyright (C) 2016 Jappie Klooster\n" +
        "This program comes with ABSOLUTELY NO WARRANTY; for details see the \n" +
        "LICENSE file. This is free software, and you are welcome to \n" +
        "redistribute it under certain conditions; see the LICENSE file for details\n"+
        "--\n"
    )
parser.add_argument(
    '--baseurl',
    default="https://distrowatch.com/",
    help="default http://distrowatch.com"
)
parser.add_argument(
    '--searchOptions',
    default="ostype=All&category=All&origin=All&basedon=All&notbasedon=None"+
    "&desktop=All&architecture=All&package=All&rolling=All&isosize=All"+
    "&netinstall=All&status=All",
    help="the GET form generates this at distrowatch.com/search.php,"+
    "everything behind the ? can be put in here, "+
    "use this to add constraints to your graph, for example if you're "+
    "only interested in active distro's, specify it at the form and copy "+
    "the resulting GET request in this argument"
)

args = parser.parse_args()

# TODO: not use this by choosing a propper html parser (
# the html.parser tries to enclose every <br> element with </br>,
# which is uneccisary and creates a huge stack. This is a workaround.
from sys import setrecursionlimit
setrecursionlimit(10000)

# for debugging...
def tohtml(lines, outFile = "output.html"):
    with open("out/%s"%outFile, "w", encoding='utf8') as f:
        f.writelines(lines)

from requests import Session
from bs4 import BeautifulSoup
session = Session()
baseurl = args.baseurl

website = session.get(
        baseurl + 'search.php?%s' % args.searchOptions
    ).text
searchSoup = BeautifulSoup(website, 'html.parser')

from re import match
def tagfilter(tag):
    return tag.name == "b" and match("[0-9]+\.", tag.text)
from logging import info
def jsondumps(item):
    import json
    return json.dumps(item, indent=4)
import strings
print("[")
# some missing root elements
godfathers = [
    "android"
]
for godfather in godfathers:
    print(jsondumps({
        strings.name:godfather,
        strings.based:strings.independend
    })+",")

foundDistributions = searchSoup.find_all(tagfilter)
for distrobution in foundDistributions:
    info("parsing %s" % distrobution.a.text)
    link = baseurl + distrobution.a.get("href")
    distrosoup = BeautifulSoup(session.get(link).text)
    structure = {
        strings.name:distrobution.a.get("href"),
        "Human Name":distrobution.a.text,
        "Link":link
    }
    anchor = distrosoup.find('ul')
    for attribute in anchor.find_all('li'):
        # I'll be happy if this works
        name = attribute.b.extract().text[:-1]
        structure[name] = attribute.text[1:].replace("\\n","")
    comma = ","
    if foundDistributions[-1] == distrobution:
        comma = ""
    print("%s%s"% (jsondumps(structure),comma))

print("]")
