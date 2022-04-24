import re
import os
import sys
import argparse


def get_steam_path():
    path = ""

    if sys.platform.startswith("linux"):
        path = os.path.join(os.getenv("HOME"), ".local/share/Steam/")
    elif sys.platform.startswith("win32"):
        path = os.path.join(os.getenv("ProgramFiles(x86)"), "Steam/")
    elif sys.platform.startswith("darwin"):
        print("П*дарас ?")
        exit(1)

    if not os.path.exists(path):
        return

    return path


default_background_img = "https://images-ext-1.discordapp.net/"\
                         "external/a8azBUG29KKZb3vJWONwm7jZ0BMv7vJu2C9fG82r290/https/media.discordapp.net/attachments/"\
                         "897474331242811443/902824827629490197/baltika_devyatka.gif"

parser = argparse.ArgumentParser(description="Configure your Steam.")

parser.add_argument("-i", "--background_url", default=default_background_img, help="Background URL.")
parser.add_argument("-b", "--background_blur", default=1, type=int, help="Blur effect.")
parser.add_argument("-n", "--hide_news", default=0, type=int, help="Hide news.")
parser.add_argument("-p", "--steam_path", default=get_steam_path(), help="Steam path.")

args = parser.parse_args()


def minimize_css(css):
    chars_blacklist = ("\t", "\n", " ")
    return "".join(filter(lambda c: c not in chars_blacklist, css))


def replace_css(selector, body, css):
    match = re.search(selector + r"[^{]*{([^}]*)}", css, flags=re.MULTILINE)

    if not match:
        return css

    print("Found {0}".format(selector))

    return body.join([css[:match.start(1)], css[match.end(1):]])


if args.steam_path is None:
    print("Steam is not found. Use the '--steam_path' argument.")
    exit(1)

steamui_path = os.path.join(args.steam_path, "steamui/css/")

if not os.path.exists(steamui_path):
    print("Not found directory '{0}'".format(steamui_path))
    exit(1)

css_files = os.listdir(steamui_path)

for css_file_path in css_files:
    css_file_path = os.path.join(steamui_path, css_file_path)

    print("Patching '{0}'".format(css_file_path))

    with open(css_file_path, "tr", encoding="utf-8") as css_file:
        css_code = css_file.read()

        css_code = replace_css(
            selector=".library_AppDetailsTransitionGroup_",
            body=minimize_css(
                '''
                    position:relative;
                    top:0;
                    left:0;
                    width:100%;
                    height:100%;
                    overflow:hidden;
                    background:#22242a;
                    background: url("{0}");
                    background-size: cover;
                '''.format(args.background_url)
            ),
            css=css_code
        )

        css_code = replace_css(
            selector=".libraryhome_UpdatesContainer_",
            body="background: transparent;",
            css=css_code
        )

        css_code = replace_css(
            selector=".libraryhome_LibraryHome_",
            body="background: transparent;",
            css=css_code
        )

        css_code = replace_css(
            selector=".libraryhome_Container_",
            body=minimize_css(
                '''
                    background: rgba(0,0,0,{0});
                    height: 100vh;
                    backdrop-filter: blur({1}px);
                '''.format(".1", args.background_blur)
            ),
            css=css_code
        )

        css_code = replace_css(
            selector=".pageablecontainer_PageableContainer_",
            body=minimize_css(
                '''
                    opacity: 1;
                    display:{0};
                '''.format("block" if args.hide_news == 0 else "none")
            ),
            css=css_code
        )

    with open(css_file_path, "tw", encoding="utf-8") as css_file:
        css_file.write(css_code)
