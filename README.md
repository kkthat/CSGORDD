
# CSGO Replay Downloader Docker

With this pre-PRE-Alpha docker container made by a wannabe coder so you can automatically download your csgo demos from valve offical MM servers.

You can find the github page [here](https://github.com/kkthat/CSGORDD)\
You can also the docker hub page [here](https://hub.docker.com/r/kkthat/csgordd)

I ask you not to laugh too hard at the code, It can be sensitive

## Read First

It is important you read this first before setting up the container.

First. I recommend you make a seperate account just for this container, I know its annoying but there is a reason, The way this contaier works is by logging into the steam account you provide login details for and "starting" csgo. when it does this its important for there not to be anyone using the account. Because if you are in game when this happes it could kick you from the match and stop the container from working.

Second. If you do make a account just for this i also recommend you spend £4~ so your account isnt limited, Then you can use that account for the steam api key aswell. Although this is optional.

Third. If you have 2FA enabled on your bot steam account then you will need to get its secret. You can get access to this by setting up your steam authenticator with [Steam Desktop Authenticator](https://github.com/Jessecar96/SteamDesktopAuthenticator) and copying the contents of the .maFile inside the maFiles directory. It should have your bots SteamID64 as its name (i.e 69696969696969420.maFile) just make sure when setting up the authenticator that you DO NOT Encrypt the authenticator. If you do you will have to remove the authenticator and re-set it up. Once you have this file paste its contents into a file called "secret.json" and put it in your binded config folder.

## Deployment

Here is a example docker compose file

```bash
version: '3.3'
services:
  csgordd:
      environment:
          - APIKEY=yourapikey
          - STEAMID=yoursteamid
          - STEAMIDKEY=yourauthcode
          - KNOWNSHARECODE=yourknownsharecode
          - USERNAME=username
          - PASSWORD=password
          - WAITTIME=60
          - FINISHEDWAITTIME=1200
          - ENABLEDEBUGGING=FALSE
          - DOWNLOADSPEED=0
      volumes:
        - /path/to/storage/config:/config
        - /path/to/storage/demos:/downloadeddemos
      image: kkthat/csgordd:latest
```

## Environment Variables

To run csgordd you will need to edit the following environment variables in your docker compose file

`APIKEY` You can get this from [here](https://steamcommunity.com/dev/apikey)

`STEAMID` This is your SteamID64

`STEAMIDKEY` This is your match history auth code. You can get this by going [here](https://help.steampowered.com/en/wizard/HelpWithGameIssue/?appid=730&issueid=128&transid=1550848375418925480&line_item=1550848375418925482) or by going to "Steam Support > CSGO > Manage my authentication codes > Access to Your Match History"

`KNOWNSHARECODE` This is a share code from any match in your accessable history in game. When copied it should look along the lines of this. (steam://rungame/730/69696969696969420/+csgo_download_match%CSGO-qRVCa-59KXh-mpgLs-Tjfkq-zweHN) You just want this part. (CSGO-qRVCa-59KXh-mpgLs-Tjfkq-zweHN)

`USERNAME` Your steam accounts username. [READ THIS FIRST](#read-first)

`PASSWORD` Your steam accounts password. [READ THIS FIRST](#read-first)

`WAITTIME` This is the interval the program waits after downloading a demo. Default is 60 seconds

`FINISHEDWAITTIME` This is the interval the program waits after downloading all demos. Default is 1200 seconds / 20 minutes

`ENABLEDEBUGGING` When set to TRUE this will enable the debug output. Default is FALSE

`DOWNLOADSPEED` This is your download speed limit in mbps. Default is 0