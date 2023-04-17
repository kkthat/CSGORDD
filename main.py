from steam.guard import SteamAuthenticator
from steam.client import SteamClient
from csgo.client import CSGOClient
import requests
import logging
import time
import json
import re
import os

# Define variables as docker environment variables
apikey = os.environ['APIKEY']
steamid = os.environ['STEAMID']
steamidkey = os.environ['STEAMIDKEY']
knownsharecode = os.environ['KNOWNSHARECODE']
accountusername = os.environ['USERNAME']
accountpassword = os.environ['PASSWORD']
FINISHEDWAITTIME = os.environ['FINISHEDWAITTIME']
WAITTIME = os.environ['WAITTIME']
ENABLEDEBUGGING = os.environ['ENABLEDEBUGGING']

# Define the name of the demos folder and files to save the codes and urls to
two_factor_secret_file = "/config/secret.json"
codesfilename = "/config/saved_codes.txt"
demosfolder = "/downloadeddemos"
# ^^ You shouldnt need to change theses but if for whatever reason you need to do so here
# just remember to also change it in the docker file if you are building from scratch :>

# Dont Change This \/
dictionary = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefhijkmnopqrstuvwxyz23456789"

# Ignore this its just to make the wait time variables intigers
FINISHEDWAITTIMEINT = int(FINISHEDWAITTIME)
WAITTIMEINT = int(WAITTIME)
# Ignore this too its to make sure the printed times are strings
FINISHEDWAITTIMESTR = str(FINISHEDWAITTIME)
WAITTIMESTR = str(WAITTIME)
# Ignore this aswell its for checking if debugging is enabled or not
ENABLEDEBUGGINGSTR = str(ENABLEDEBUGGING)
if ENABLEDEBUGGINGSTR == "TRUE":
    print("Debugging Enabled!!")
    logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
else:
    pass
# Ignore this also its to check if a 2fa file is found and enable the 2fa login stuff
    if os.path.isfile(two_factor_secret_file):
        two_f_a_detected = 1
        print("2FA Detected")
        secrets = json.load(open(two_factor_secret_file))
        sa = SteamAuthenticator(secrets)
        account2fa = sa.get_code()
    else:
        two_f_a_detected = 0
        print("2FA NOT Detected")

# Talk to steam API to get next match share code
def get_next_match_code(apikey, steamid, steamidkey, knownsharecode):

    # Now, let's open the file and read its contents into a list
    with open(codesfilename, "r") as f:
        codes = f.read().splitlines()

    # Check if knownsharecode is already in the list
    if knownsharecode in codes:
        # If it is, find the last code in the list and make it a variable
        last_code = codes[-1]
    else:
        # If it's not, append it to the end of the list
        codes.append(knownsharecode)
        # And write the updated list back to the file
        with open(codesfilename, "w") as f:
            f.write("\n".join(codes) + "\n" )

        # Since we just added the code to the end of the list, we can set last_code to be equal to knownsharecode
        last_code = knownsharecode

    # Talk to api and get next match code
    url = "https://api.steampowered.com/ICSGOPlayers_730/GetNextMatchSharingCode/v1?key=" + apikey + "&steamid=" + steamid +"&steamidkey=" + steamidkey + "&knowncode=" + last_code
    apiget = requests.get(url)

    # Parse api response
    api_json_parse = apiget.text
    data = json.loads(api_json_parse)
    nextcode = data['result']['nextcode']

    # If nextcode is "N/A", Raise exeption
    if nextcode == "n/a":
        raise ValueError("No newer match codes available.")

    # Check if the code parsed is valid
    if not re.match(r'^(CSGO)?(-?[%s]{5}){5}$' % dictionary, nextcode):
        raise ValueError("Invalid share code")

    # Save the next code to a file
    with open(codesfilename, "a") as f:
        f.write(nextcode + "\n")

    # Update the last code variable and return the last code
    last_code = nextcode
    return last_code

# Decode share code provided from api
def decode_match_sharing_code(nextcode):

    # Check if the code parsed is valid
    if not re.match(r'^(CSGO)?(-?[%s]{5}){5}$' % dictionary, nextcode):
        raise ValueError("Invalid share code")

    # Remove "CSGO-" and any "-" from the code
    nextcode = re.sub('CSGO\-|\-', '', nextcode)[::-1]

    # Decode the match sharing code
    a = 0
    for c in nextcode:
        a = a*len(dictionary) + dictionary.index(c)

    _bitmask64 = (1 << 64) - 1

    def _swap_endianness(x):
        y = 0
        while x > 0:
            y = (y << 8) | (x & 0xff)
            x >>= 8
        return y

    # Call this function ^^ to swap the byte order
    a = _swap_endianness(a)
    6
    decodedresult = {
        'matchid':   a        & _bitmask64,
        'outcomeid': a >> 64  & _bitmask64,
        'token':     a >> 128 & 0xFFFF
    }
    
    # Seperate Into Seperate Variables
    seperateresult = decodedresult
    sepmatchid = seperateresult['matchid']
    sepoutcomeid = seperateresult['outcomeid']
    septoken = seperateresult['token']

    return sepmatchid, sepoutcomeid, septoken

# Talk to CSGO GC to get the url for the demo file
def run_csgo_match_info(accountusername, accountpassword, inputmatchid, inputoutcomeid, inputtoken):

    client = SteamClient()
    cs = CSGOClient(client)

    @client.on('logged_on')
    def start_csgo():
        cs.launch()

    @cs.on('ready')
    def gc_ready():
        time.sleep(1)
        # Ask GC for info on requested match
        cs.request_full_match_info(inputmatchid, inputoutcomeid, inputtoken)
        # Mark response as a string
        unparsedurl = (str) (cs.wait_event('full_match_info'))
        # Parse the string for any HTTP/S links
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        parsedurl = re.findall(url_pattern, unparsedurl)
        cleanurl = parsedurl[0]
        # Clean the URl of ['']
        cleanedparsedurl = cleanurl.replace("[", "").replace("]", "").replace("'", "")
        return cleanedparsedurl

    # hopefully restart in 2 mins if steam cannot be accessed
    while True:
        try:
            if two_f_a_detected == 1:
                client.login(username=accountusername, password=accountpassword, two_factor_code=account2fa)
                return gc_ready()
            else:
                client.login(username=accountusername, password=accountpassword)
                return gc_ready()
        except EOFError:
            print("An EOFError has occurred, most likely a error connecting to steam")
            print("Waiting 2 minutes then retrying")
            time.sleep(120)
            continue

# Download the demo file and save it
def download_demo(finalurl):
    
    # Get file name from url
    demoname = finalurl.split("/")[-1]

    # set the path and filename of the downloaded file
    download_file_path = os.path.join(demosfolder, demoname)

    # check if the file already exists
    if os.path.isfile(download_file_path):
        print('Demo already exists.')
    else:
        # if file does not exist, download it
        print('Downloading demo...')
        response = requests.get(finalurl)
        with open(download_file_path, 'wb') as f:
            f.write(response.content)
        print('Demo downloaded.')


while True:

    # Get latest share code
    try:
        latestcode = get_next_match_code(apikey, steamid, steamidkey, knownsharecode)
    except ValueError as ErrorNoMoreCodes:
        print(ErrorNoMoreCodes)
        print("Waiting for " + FINISHEDWAITTIMESTR + " seconds before running again")
        time.sleep(FINISHEDWAITTIMEINT)
        continue
    
    # Decode latest share code
    sepmatchid, sepoutcomeid, septoken = decode_match_sharing_code(latestcode)

    # Get download url
    finalurl = run_csgo_match_info(accountusername, accountpassword, sepmatchid, sepoutcomeid, septoken)

    # Print stuff
    print("Sharing Code : " + latestcode)
    print("Download Url: " + finalurl)

    # Download the demo as a zip
    download_demo(finalurl)

    # Loop code again
    print("Waiting " + WAITTIMESTR + " seconds before running again")
    time.sleep(WAITTIMEINT)