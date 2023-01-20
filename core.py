import json
import random
import asyncio
import websockets
import threading
import time

SERVERIP = "0.0.0.0"
SERVERPORT = 9999
DATAFILE = "./database.json"
CMD_LOGIN = "!"
CMD_COMMAND = ">"
NEWUSERCONFIG = {"chicken": 10, "coin": 0}
HELP = \
'''help   : *
info   : your information
gr     : get random chicken
'''

DEBUG = False

def pushmsg(text):
    return "<%s" % text

def errormsg(text):
    return "!%s" % text

class Farmer:
    def __init__(self):
        pass

    def __repr__(self):
        if (hasattr(self, "account")):
            return "<Farmer '%s'>" % self.account
        return "<Farmer Null>"

class Hcf:
    def __init__(self):
        self.database = self._load_data()
        # {websocket object: farmer object}
        self.op = {}
        # auto update database, every 10 seconds
        autoupdate = threading.Thread(target = self._update_database)
        autoupdate.setDaemon(True)
        autoupdate.start()

    # update database.json
    def _update_database(self):
        while (True):
            database = {}
            for o in self.database:
                database[o.account] = o.__dict__
            with open(DATAFILE, "w") as fp:
                json.dump(database, fp, indent = 4)
            time.sleep(10)

    # load database.json
    def _load_data(self):
        with open(DATAFILE, "r") as fp:
            res = json.load(fp)
        newres = []
        for u, d in res.items():
            obj = Farmer()
            for k, v in d.items():
                setattr(obj, k, v)
            newres.append(obj)
        return newres
 
    # add new farmer to database
    # account = xxx, password = xxx, info1 = xxx, info2 = xxx
    def _add_farmer(self, account, password, **info):
        obj = Farmer()
        obj.account = account
        obj.password = password
        for k, v in info.items():
            setattr(obj, k, v)
        self.database.append(obj)

    # find farmer object by account
    # not found: None
    def _find_by_account(self, account):
        for farmer in self.database:
            if (farmer.account == account):
                return farmer;
        return None;

    # set op
    def _setop(self, websocket, farmer):
        self.op[websocket] = farmer;

    # find farmer object by websocket
    def _find_by_websocket(self, websocket):
        for w, f in self.op.items():
            if (w == websocket):
                return f;
        return None;

    # handle and return reply data
    def _handledata(self, data, websocket):
        if (len(data) <= 0):
            return errormsg("error format")
        cmd = data[0]
        if (len(data) >= 2):
            content = data[1:]
        else:
            content = ""
        
        # login in
        if (cmd == CMD_LOGIN):
            accpwd = content.split()
            if (len(accpwd) == 2):
                account = accpwd[0]
                password = accpwd[1]
                farmer = self._find_by_account(account)
                if (farmer == None):
                    self._add_farmer(account, password, **NEWUSERCONFIG)
                    farmer = self._find_by_account(account)
                    self._setop(websocket, farmer);
                    return pushmsg("welcome, %s! enjoy raising chicken!" % account)
                else:
                    if (farmer.password == password):
                        self._setop(websocket, farmer);
                        return pushmsg("welcome, %s!" % account)
                    else:
                        return errormsg("wrong password")
            else:
                return errormsg("error format")

        # normal command
        if (cmd == CMD_COMMAND):
            farmer = self._find_by_websocket(websocket)
            if (farmer == None):
                return errormsg("please login in first")

            command = content.split()
            if (command == []):
                return pushmsg("don't send null")

            if (command[0] == "help"):
                return pushmsg(HELP)

            elif (command[0] == "gr"):
                num = random.randint(1, 3)
                farmer.chicken += num
                return pushmsg("you get %d chicken" % num)

            elif (command[0] == "info"):
                r = "%s:\nchicken:%s\ncoin:%s" % (farmer.account, farmer.chicken, farmer.coin)
                return pushmsg(r)

        return pushmsg("?")

    # receive data
    async def _recv(self, websocket):
        try:
            while (True):
                data = await websocket.recv()
                print("client:", data)
                reply = self._handledata(data, websocket)
                print("server:", reply)
                await websocket.send(reply)
        except websockets.exceptions.ConnectionClosedOK:
            pass

    async def run(self):
        async with websockets.serve(self._recv,
                                    SERVERIP,
                                    SERVERPORT):
            await asyncio.Future()

if __name__ == "__main__":
    hcf = Hcf()
    if (DEBUG == False):
        asyncio.run(hcf.run())
