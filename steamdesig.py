import re
import os
import sys
import argparse
import json
import urllib.request

if sys.platform.startswith("win32"):
    import winreg


# Get steam path
#   get steam path
def get_steam_path():
    path = ""
    if sys.platform.startswith("linux"):
        path = os.path.join(os.getenv("HOME"), ".local/share/Steam/")
    elif sys.platform.startswith("win32"): 
        temp_steampath = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                                            r"Software\Valve\Steam"),
                                                            "SteamPath")[0] + "/"
        path = temp_steampath
    elif sys.platform.startswith("darwin"):
        print("Извините, *ваша* система не поддерживает игровую платформу Steam!\n"\
              "                                         No 32-bit libs? (c) 2022-2023")
        sys.exit(1)

    if not os.path.exists(path):
        return
    return path

# VKPlay API
#   getting vkplay json via api
def vkplay_api_get_wallpaper(input_something):
    vk_gc_id_alt = ''
    vk_gc_id = ''
    vk_slug = ''
    vk_game_api_get_format = "https://api.vkplay.ru/play/games/get/?full_cost_info=1&check_register=1"

    try:
        if '/' in input_something:
            if '://' not in input_something:
                input_something = 'https://' + input_something #just to make it parse.
            
            #parse the link
            vk_slug = [i for i in input_something.split('/') if i][4]
            
        elif (input_something.startswith('0.') or input_something.startswith('0_')):
            # allow to input the raw GC ID by hand
            vk_gc_id_alt = input_something.replace('_', '.')
            vk_gc_id = vk_gc_id_alt.replace('.', '_')

        else:
            # allow to specify the slug directly by hand
            vk_slug = input_something
    except Exception as error:
        print('VKPlay API # Wrong url/gameid.')
        return error
        
    if vk_gc_id_alt != '':
        vk_game_api_url = vk_game_api_get_format + f'&gcid={vk_gc_id_alt}'
    else:
        vk_game_api_url = vk_game_api_get_format + f'&slug={vk_slug}'

    try:
        vk_game_api_get_format = urllib.request.urlopen(vk_game_api_url)
    except Exception as error:
        print("VKPlay API # Error in getting json!")
        return error

    vk_game_api_json = json.load(vk_game_api_get_format)['wallpaper']
    
    return vk_game_api_json

# Useful shit
#   -
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

# Useful shit for css
#   -
def minimize_css(css):
    chars_blacklist = ("\t", "\n", " ")
    return "".join(filter(lambda c: c not in chars_blacklist, css))

def replace_css(selector, body, css):
    match = re.search(selector + r"[^{]*{([^}]*)}", css, flags=re.MULTILINE)

    if not match:
        return css

    print(f"Found {selector}")

    return body.join([css[:match.start(1)], css[match.end(1):]])


# Default values and args
DEFAULT_BACKGROUND_IMG = "https://raw.githubusercontent.com/Michael-Soyka/steam-lib-designer/"\
                        "master/_resources/blank_wp.gif"
IN_EDITING = False

parser = argparse.ArgumentParser(description="Configure your Steam.")

parser.add_argument("-i", "--background_url",
                    default=DEFAULT_BACKGROUND_IMG, help="Background URL.")
parser.add_argument("-b", "--background_blur",
                    default=1, type=int, help="Background blur effect.")
parser.add_argument("-d", "--background_darkness",
                    default=0.2, type=float, help="Background dark effect.")
parser.add_argument("-n", "--hide_news",
                    action="store_true", help="Hide news.")
parser.add_argument("-p", "--steam_path",
                    default=get_steam_path(), help="Steam path.")
parser.add_argument("-vk", "--vkplay_wallpaper",
                    default=None, help="VKplay Game Wallpaper")

args = parser.parse_args()

# Steam Path
if args.steam_path is None:
    print("Steam is not found. Use the '--steam_path' argument.")
    exit(1)

steamui_path = os.path.join(args.steam_path, "steamui/css/")

if not os.path.exists(steamui_path):
    print(f"Not found directory '{steamui_path}'")
    sys.exit(1)

def get_all_files(directory):
    for dirpath,dirnames,filenames in os.walk(directory):
        for files in filenames:
            yield os.path.abspath(os.path.join(dirpath, files))

css_files = [*get_all_files(steamui_path)]

# Set background url
background_image_url = args.background_url
if args.vkplay_wallpaper is not None:
    background_image_url = vkplay_api_get_wallpaper(args.vkplay_wallpaper)

# Main code
for css_file_path in css_files:
    if not IN_EDITING:
        with open(steamui_path + "sld_temp_file", "w", encoding='UTF-8') as temp_reload_file:
            temp_reload_file.write("SteamLibDesigner temp file")
            temp_reload_file.close()
        IN_EDITING = True

    css_file_path = os.path.join(steamui_path, css_file_path)
    print("                " + css_file_path)

    print(f"Patching '{css_file_path}'")

    with open(css_file_path, "tr", encoding="utf-8") as css_file:
        css_code = css_file.read()
        print(css_file)

        css_code = replace_css(
            ".library_AppDetailsTransitionGroup_",
            minimize_css(
                f'''
                    position:relative;
                    top:0;
                    left:0;
                    width:100%;
                    height:100%;
                    overflow:hidden;
                    background:#22242a;
                    background: url("{background_image_url}");
                    background-size: cover;
                '''
            ),
            css_code
        )

        css_code = replace_css(
            ".libraryhome_UpdatesContainer_",
            minimize_css(f'''
                        background: transparent;
                        {"height: 0px !important;" if args.hide_news else ""}
                    '''),
            css_code
        )

        css_code = replace_css(
            ".libraryhome_LibraryHome_",
            "background: transparent;",
            css_code
        )

        css_code = replace_css(
            ".libraryhome_Container_",
            minimize_css(
                f'''
                    background: rgba(0,0,0,{args.background_darkness});
                    height: 100vh;
                    backdrop-filter: blur({args.background_blur}px);
                '''
            ),
            css_code
        )

        css_code = replace_css(
            ".pageablecontainer_PageableContainer_",
            minimize_css(
                f'''
                    opacity: 1;
                    display:{"none" if args.hide_news else "block"};
                '''
            ),
            css_code
        )

    with open(css_file_path, "tw", encoding="utf-8") as css_file:
        css_file.write(css_code)

os.remove(steamui_path + "sld_temp_file")

print(f'''
   l       ++        +++-    dDd       HHHHHH     sSSS   H H       GGGG
  l+               -++ +l    D  Dd     H        sSS      hHh     GGG  +G
  l        i       b   l     D    d    H        S         h     GG
 +l        i      b  +l      D     d   H        sSS             G
 l        i+     b +l        D     D   HHHHH      sSS     H     G
l     ++  i    b++++++-      D     D   H            sS    H     G
l  ++    i+  bbl+    ++      D     d   H             SS   H     G    +G+G+
l++      i     l+   ++       D    d    H            SSs   H     GGG    GG
+              -+++-         dDDDd     HHHHHH   SSSSs     H       GGGGGG

            ⊱ Xendot, Solyanka, Shelest, MichaelSoyka ⊰
                            2022-2023

                    Thanks u {os.getlogin()} 4 using!
''')
