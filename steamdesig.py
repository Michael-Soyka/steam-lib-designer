import re
import argparse




parser = argparse.ArgumentParser(description='Redesig ur steam')

parser.add_argument("-bgdark", type=int, default=0, help="bg dark am [1 - 9]")
parser.add_argument("-blur", type=int, default=25, help="bg blur am")
parser.add_argument("-news", type=int, default=1, help="toggle news tab")
parser.add_argument("-bgsize", default="cover", help="bg size")
parser.add_argument("-bgurl", default="https://d3gz42uwgl1r1y.cloudfront.net/rh/rhyu/submission/2016/09/48807118a7ef82fbf6fb512c31fc2fe9.png", help="bgurl")
parser.add_argument("-path", default="C:\\Program Files (x86)\\Steam\\", help="steam path")

args = parser.parse_args()
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

bgsize = args.bgsize
steampath = args.path
bgurl = args.bgurl
newstoggle = args.news
bluram = args.blur
dark = clamp(args.bgdark/10, 0, 0.9)

steamcss6 = steampath + "steamui\\css\\6.css"
steamcss1 = steampath + "steamui\\css\\1.css"
steamcsslib = steampath + "steamui\\css\\library.css"


if newstoggle == 1:
    newsmod = "none"
else:
    newsmod = "block"




regex_match_rule0 = re.compile(
    r"(\.library_AppDetailsTransitionGroup_[^{]+)\{(.*)\}",
    re.MULTILINE)

regex_match_rule1 = re.compile(
    r"(\.libraryhome_UpdatesContainer_[^{]+)\{(.*)\}",
    re.MULTILINE)

regex_match_rule2 = re.compile(
    r"(\.libraryhome_LibraryHome_[^{]+)\{(.*)\}",
    re.MULTILINE)

regex_match_rule3 = re.compile(
    r"(\.libraryhome_Container_[^{]+)\{(.*)\}",
    re.MULTILINE)

regex_match_rule4 = re.compile(
    r"(\.pageablecontainer_PageableContainer_[^{]+)\{(.*)\}",
    re.MULTILINE)




def replace_rule0(match):
    inner = match[2]
    inner = "position:relative;top:0;left:0;width:100%;height:100%;overflow:hidden;background:#22242a;" + "background: url(" + '"' + bgurl + '"' + "); background-size: cover;"
    return "%s{%s}" % (match[1], inner)


def replace_rule1(match):
    inner = match[2]
    inner = "background: transparent;"
    return "%s{%s}" % (match[1], inner)

def replace_rule1a(match):
    inner = match[2]
    inner = "background: rgba(0,0,0," + str(dark) + "); height: 100vh; backdrop-filter: blur( " + str(bluram) + "px);"
    return "%s{%s}" % (match[1], inner)

def replace_rule2(match):
    inner = match[2]
    inner = "opacity: 1; display:" + newsmod + ";"
    return "%s{%s}" % (match[1], inner)




def replace_style0(style):
    return regex_match_rule0.sub(replace_rule0, style)


def replace_style1(style):
    return regex_match_rule1.sub(replace_rule1, style)
def replace_style1a(style):
    return regex_match_rule2.sub(replace_rule1, style)


def replace_style2(style):
    return regex_match_rule3.sub(replace_rule1a, style)

def replace_style3(style):
    return regex_match_rule4.sub(replace_rule2, style)




with open (steamcss6, 'r') as f:

    old_data = f.read()

    new_data = replace_style1(old_data)

    new_data = replace_style1a(new_data)

    new_data = replace_style2(new_data)

with open (steamcss6, 'w') as f:
  f.write(new_data)

#---

with open (steamcsslib, 'r') as f:

    old_data = f.read()

    new_data = replace_style0(old_data)

with open (steamcsslib, 'w') as f:
  f.write(new_data)

#---

with open (steamcss1, 'r') as f:

    old_data = f.read()

    new_data = replace_style3(old_data)

with open (steamcss1, 'w') as f:
  f.write(new_data)
  

print("Sexfull")