import time, requests, hashlib, random, json, os, subprocess, sys, threading, traceback, pickle, math
from datetime import datetime
from decimal import Decimal
from base64 import b16decode, b16encode
from time import sleep
from copy import deepcopy
from collections import Counter
from pprint import pprint
from functools import lru_cache
import eth_abi
FOLDER = os.path.abspath(os.path.dirname(__file__))
if os.path.isfile(FOLDER+"/.env"):
    for line in open(FOLDER+"/.env"):
        line = line.strip()
        if not line:
            continue
        if "=" not in line or len(line.split("="))!=2:
            print("[ERROR] wrong .env line:", line)
        k, v = line.split("=")
        os.environ[k] = v
sess=requests.session()
def toi(i):
    if isinstance(i, int):
        return i
    if i.startswith("0x"):
        return int(i,16)
    return int(i)
YEAR = 365*86400

CHAINRPCS = {
        "Ethereum": ["https://eth-mainnet.alchemyapi.io/v2/jn3PI8En2phQwdeFAaQ6LK2aexudYJs5", "https://apis.ankr.com/bfb13191a1de469d86472cbc24adef98/54d69cace207b0e78d72c79fb28598a0/eth/fast/main", "https://dreamy-curie:ended-thrive-pecan-unsnap-cupped-shady@nd-052-809-299.p2pify.com/", "https://ethereum-mainnet--rpc.datahub.figment.io/apikey/38e33f901e9eda411a8cc9b85164cd79/", "https://erigon-mainnet--rpc.datahub.figment.io/apikey/38e33f901e9eda411a8cc9b85164cd79", "https://rpc.flashbots.net/", "https://ethereumnodelight.app.runonflux.io", "https://eth.getblock.io/mainnet/?api_key=15bc61a2-3677-4e90-b243-53a3fd6f0fab", "https://mainnet.infura.io/v3/a45f7ab372124312b0c1c2c93abd21cf", "https://main-rpc.linkpool.io/", "https://main-light.eth.linkpool.io/", "https://nodes.mewapi.io/rpc/eth", "https://api.mycryptoapi.com/eth", "https://api.myetherwallet.com/eth", "https://eth-mainnet.nodereal.io/v1/f170019bceec46158207638ed35553b7", "https://eth-mainnet.gateway.pokt.network/v1/5f9180e3b90218002e9cea69", "https://eth-archival.gateway.pokt.network/v1/60a29db1ff3a4800349d2407", "https://still-nameless-star.quiknode.pro/"] + ["https://eth.getblock.io/mainnet/?api_key=3d10f1d2-eebc-4ad4-8a8a-33fbeb3481dc",        "https://still-nameless-star.quiknode.pro/",        "https://white-bitter-breeze.quiknode.pro/a53ae019bc2182e0a144c51f8c04a2d6687cecb6/",        "https://eth-mainnet.gateway.pokt.network/v1/5f9180e3b90218002e9cea69",        "https://eth-archival.gateway.pokt.network/v1/60a29db1ff3a4800349d2407",        "https://speedy-nodes-nyc.moralis.io/b9aed21e7bb7bdeb35972c9a/eth/mainnet/archive",        "https://apis.ankr.com/e62bc219f9c9462b8749defe472d2dc5/6106d4a3ec1d1bcc87ec72158f8fd089/eth/archive/main",        "https://mainnet.infura.io/v3/98062ebb00754df2ae2911a2db0be28b",        'https://mainnet.infura.io/v3/a1743f084f8a46bfb3696389eeb9f217',        'https://mainnet.infura.io/v3/cad7f83b4e47462e90387487530239af',        'https://mainnet.infura.io/v3/01e4876c179a49ebbf8ad09f7037d9ee',        'https://mainnet.infura.io/v3/483c1730b99b46729c7f82f49302bbf8',        'https://mainnet.infura.io/v3/fa3e2193dfcb48978f731fadf8a1282a',        'https://mainnet.infura.io/v3/139b233124ca4a7cb78ac63cd0a2d29f',        'https://mainnet.infura.io/v3/e846fc35019a4766babcc4e9e757bb74',        'https://mainnet.infura.io/v3/b838cc16e73f482b960d1f86c05533a6',        'https://mainnet.infura.io/v3/4ca56581b1234f2a9cf4b7333c1f8ac1',        'https://mainnet.infura.io/v3/d266a83cc83a40d7b14257be4579d310', 'https://mainnet.infura.io/v3/483c1730b99b46729c7f82f49302bbf8', 'https://mainnet.infura.io/v3/d266a83cc83a40d7b14257be4579d310', "https://apis.ankr.com/bfb13191a1de469d86472cbc24adef98/54d69cace207b0e78d72c79fb28598a0/eth/fast/main",],
        "BSC":["https://bsc-dataseed.binance.org/", "https://bsc-dataseed.binance.org/", "https://bsc.getblock.io/mainnet/?api_key=15bc61a2-3677-4e90-b243-53a3fd6f0fab", "https://proud-patient-forest.bsc.quiknode.pro/8fffb4d84f42ec02686c35631b566c819138e876/", "https://apis.ankr.com/aca3f90e4ca54adc9340fac644770124/54d69cace207b0e78d72c79fb28598a0/binance/full/main", ], #['https://speedy-nodes-nyc.moralis.io/b9aed21e7bb7bdeb35972c9a/bsc/mainnet/archive', 'https://bsc.getblock.io/mainnet/?api_key=91f8195f-bf46-488f-846a-73d6853790e7', 'https://bsc.getblock.io/mainnet/?api_key=5218d45d-da20-459a-8f40-3e65c2540e8b', 'https://bsc.getblock.io/mainnet/?api_key=660a41be-e64a-4519-a8b6-0a2d3dfc2882', 'https://bsc.getblock.io/mainnet/?api_key=c7d17503-99e5-489f-9a9d-3673b9494b63', 'https://bsc.getblock.io/mainnet/?api_key=65f1d98d-ac5a-45f8-be38-00ca29126f92']
        "OKxChain":["https://apis.ankr.com/ac809fe694fb4c3c8f499329dde5ea94/694969b03a802598e127f91071f9e24d/okexchain/full/main", "https://exchainrpc.okex.org/"],
        "Gnosis":["https://apis.ankr.com/1c14dc62e85d4c12a2e64485c8330c63/694969b03a802598e127f91071f9e24d/xdai/fast/main", "https://rpc.xdaichain.com/"],
        "Heco":["https://apis.ankr.com/3ed69ca631cd4ee58a000dd954bd7a89/694969b03a802598e127f91071f9e24d/heco/fast/main", "https://http-mainnet.hecochain.com"],
        "Polygon":["https://rpc.ankr.com/polygon", "https://public-rpc.blockpi.io/http/polygon", "https://matic-mainnet-full-rpc.bwarelabs.com", "https://matic-mainnet.chainstacklabs.com", "https://matic-mainnet--jsonrpc.datahub.figment.io/apikey/38e33f901e9eda411a8cc9b85164cd79/", "https://matic.getblock.io/mainnet/?api_key=15bc61a2-3677-4e90-b243-53a3fd6f0fab", "https://rpc-mainnet.maticvigil.com/v1/9cdf203c46d3a7b7f1bdaa0a7e624133da091a8d", "https://rpc-mainnet.maticvigil.com", "https://poly-mainnet.gateway.pokt.network/v1/lb/623bec216297a1003ae0c766", "https://poly-archival.gateway.pokt.network/v1/lb/623bec216297a1003ae0c766", "https://rpc-mainnet.matic.quiknode.pro"]+["https://matic-mainnet--jsonrpc.datahub.figment.io/apikey/5688e5f9d801f1c1f8f64af205f0594a/", "https://rpc-mainnet.maticvigil.com/", "https://rpc-mainnet.matic.network"], #['https://polygon-mainnet.g.alchemy.com/v2/hIxdOaBwG94gu6FlhQpCP5lWuzBOLvmt', 'https://polygon-mainnet.g.alchemy.com/v2/NDsioMXTwci91lMdODnh3iBbcJoxCgy8', 'https://polygon-mainnet.infura.io/v3/daaa68ec242643719749dd1caba2fc66', 'https://speedy-nodes-nyc.moralis.io/f2963e29bec0de5787da3164/polygon/mainnet/archive', 'https://rpc-mainnet.maticvigil.com/v1/1cfd7598e5ba6dcf0b4db58e8be484badc6ea08e', 'https://speedy-nodes-nyc.moralis.io/b9aed21e7bb7bdeb35972c9a/polygon/mainnet/archive']
        "Fantom":["https://apis.ankr.com/198767f7c91d4ab285bbcb7fe798ab83/54d69cace207b0e78d72c79fb28598a0/fantom/full/main", "https://apis.ankr.com/c3f382db4c55497b81bf3feb1e9a8499/d37735e535d9d051230799cae45aeb6a/fantom/full/main", "https://rpc.ftm.tools/"],
        "KCC":["https://rpc-mainnet.kcc.network"],
        "FSN": ["https://mainnet.anyswap.exchange", "https://fsn.dev/api"],
        "Avalanche": ["https://api.avax.network/ext/bc/C/rpc", "https://avalanche--mainnet--rpc.datahub.figment.io/apikey/b56dcd7987f05a43637a94ad98d546be/ext/bc/C/rpc", "https://apis.ankr.com/b2729e180d7e4d3e98f8c0129608448d/54d69cace207b0e78d72c79fb28598a0/avax/archive/main", ],
        "Harmony": ["https://a.api.s0.t.hmny.io", "https://rpc.s0.t.hmny.io", "https://api.harmony.one", "https://harmony-0-rpc.gateway.pokt.network", ],
        "Arbitrum":["https://arb1.arbitrum.io/rpc", "https://apis.ankr.com/7e65ebc11da541ae8b2d8a7fc30a9b5a/54d69cace207b0e78d72c79fb28598a0/arbitrum/full/main", ],
        "Optimism":["https://mainnet.optimism.io/", "https://apis.ankr.com/be5fdc9d5887403184315afa48776ba0/694969b03a802598e127f91071f9e24d/optimism/full/main", ],
        "CELO":["https://forno.celo.org",],
        "SDN": ["https://rpc.shiden.astar.network:8545", "https://shiden.api.onfinality.io/public", "https://shiden.api.onfinality.io/rpc?apikey=b3543e2d-c57c-49f9-a215-b45c331a51d0", ],
        "Moonriver": ["https://rpc.moonriver.moonbeam.network", "https://moonriver.api.onfinality.io/public", "https://pub.elara.patract.io/moonriver", "https://moonriver.api.onfinality.io/rpc?apikey=b3543e2d-c57c-49f9-a215-b45c331a51d0"],
        "Boba": ["https://mainnet.boba.network/"],
        "Cronos": ["https://evm.cronos.org", "https://evm-cronos.crypto.org", "https://cronosrpc-1.xstaking.sg"],
        "TLOS":["https://mainnet.telos.net/evm"],
        "IoTeX":["https://babel-api.mainnet.iotex.io"],
        "Fuse":["https://rpc.fuse.io"],
        "SYS":["https://rpc.syscoin.org"],
        "Metis": ["https://andromeda.metis.io/?owner=1088"],
        "MTV": ["https://rpc.mtv.ac"],
        "Moonbeam": ["https://moonbeam.api.onfinality.io/rpc?apikey=499ab348-13c8-4f4e-bebd-ce2af1141d74", "https://rpc.api.moonbeam.network", "https://moonbeam.api.onfinality.io/public", "https://moonbeam.api.onfinality.io/rpc?apikey=b3543e2d-c57c-49f9-a215-b45c331a51d0"],
        "Astar": ["https://rpc.astar.bldnodes.org/", "https://astar.api.onfinality.io/rpc?apikey=b3543e2d-c57c-49f9-a215-b45c331a51d0"],
        "Aurora":["https://mainnet.aurora.dev/5RiSEXrGNaxuFBBfype3hWRq3RTxHeAUEfYQAejmJh9j"],
        "Milkomeda":["https://rpc-mainnet-cardano-evm.c1.milkomeda.com"],
        "Oasis(Emerald)":["https://emerald.oasis.dev"],
        "HSC": ["https://http-mainnet.hoosmartchain.com", "https://http-mainnet.hoosmartchain.com", ],
}
SimpleChain = {"ETH": "Ethereum", "B":"BSC", "M":"Polygon","F":"Fantom","A":"Avalanche","Ha":"Harmony","Arb":"Arbitrum","CELO":"CELO","MOVR":"Moonriver"}
CHAINSCAN = {
    "Ethereum":  "etherscan.io",
    "BSC": "bscscan.com",
    "OKxChain": "www.oklink.com/okexchain",
    "Gnosis": "blockscout.com/xdai/mainnet",
    "Heco": "hecoinfo.com",
    "Polygon": "polygonscan.com",
    "Fantom": "ftmscan.com",
    "KCC": "explorer.kcc.io",
    "Moonriver": "blockscout.moonriver.moonbeam.network",
    "FSN": "blocks.fusionnetwork.io",
    "Avalanche": "cchain.explorer.avax.network",
    "Harmony": "explorer.harmony.one",
    "Arbitrum": "arbiscan.io",
    "Optimism":"optimistic.etherscan.io",
    "CELO":"explorer.celo.org",
    "SDN": "shiden.subscan.io",
    "Boba":"blockexplorer.boba.network",
    "Cronos":"cronos.crypto.org/explorer/",
    "TLOS":"teloscan.io",
    "Fuse":"explorer.fuse.io",
    "SYS":"explorer.syscoin.org",
    "Metis":"andromeda-explorer.metis.io",
    "MTV":"e.mtv.ac",
    "Moonbeam":"blockscout.moonbeam.network",
    "Astar": "astar.subscan.io",
    "Aurora":"explorer.mainnet.aurora.dev",
    "Milkomeda":"explorer-mainnet-cardano-evm.c1.milkomeda.com",
    "Oasis(Emerald)":"explorer.emerald.oasis.dev",
    "HSC": "hooscan.com",
}

CHAINNATIVE = {
    "Ethereum":  "ETH",
    "BSC": "BNB",
    "OKxChain": "OKT",
    "Gnosis": "DAI",
    "Heco": "HT",
    "Polygon": "MATIC",
    "Fantom": "FTM",
    "KCC": "KCC",
    "Moonriver": "MOVR",
    "FSN": "FSN",
    "Avalanche": "AVAX",
    "Harmony": "ONE",
    "Arbitrum": "ETH",
    "Optimism":"ETH",
    "CELO":"CELO",
    "SDN": "SDN",
    "Boba":"ETH",
    "Cronos":"CRO",
    "Fuse":"Fuse",
    "SYS":"SYS",
    "Metis":"METIS",
    "MTV":"MTV",
    "Moonbeam":"GLMR",
    "Astar": "ASTR",
    "Aurora":"ETH",
    "Milkomeda":"ADA",
    "Oasis(Emerald)":"ROSE",
    "HSC":"HOO",
}
CHAINID2NAME_DICT = """1:Ethereum
5:Goerli
10:Optimism
56:BNB Chain
66:OKXChain
100:Gnosis
128:Heco
137:Polygon
250:Fantom
321:KCC
336:SDN
1285:Moonriver
4689:IoTeX
32659:FSN
42220:Celo
43114:Avalanche
1666600000:Harmony
42161:Arbitrum
40:TLOS
25:Cronos
288:Boba
122:Fuse
57:SYS
1088:Metis
62621:MTV
1284:Moonbeam
592:Astar
1313161554:Aurora
2001:Milkomeda
42262:Oasis(Emerald)
70:HSC
192837465:Gather
"""
_chainid2name={i.split(":")[0]:i.split(":")[1] for i in CHAINID2NAME_DICT.strip().split("\n")}
_chainname2id={j:i for i,j in _chainid2name.items()}
class NoBlock(Exception):
    def __init__(self, text):
        self.text = text

def myprint(*args, **kwargs):
    args = list(args)
    args[0] = "["+time.strftime("%Y-%m-%d %H:%M:%S")+"] " + str(args[0])
    print(*args, **kwargs)

def rpccall(endpoint, data, timeout=10):
    if endpoint == 'https://api-geth-archive.ankr.com':
        auth = ("balancer_user", "balancerAnkr20201015")
    else:
        auth = None
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"}
    if endpoint == "https://polygon-mainnet.infura.io/v3/daaa68ec242643719749dd1caba2fc66":
        headers["Origin"] = 'https://app.balancer.fi'
    x = sess.post(endpoint, json=data, auth=auth, headers=headers, timeout=timeout)
    return x

from Crypto.Hash import keccak
def function_hash(func_str):
    return keccak.new(digest_bits=256).update(func_str.encode("utf-8")).hexdigest()[:8]
    
def addrtoarg(addr):
    if isinstance(addr, int):
        addr = hex(addr)
    if addr.startswith("0x"):
        addr = addr[2:]
    return addr.lower().rjust(64, "0")
toarg = addrtoarg

def callfunction(endpoint, addr, func_str, args_str, blockid="latest", returnint=True):
    if os.environ.get("DEBUG", False):
        print("[callfunction]", addr, func_str, "0x"+function_hash(func_str)+args_str, end="", flush=True)
    try:
        height = hex(int(blockid))
    except:
        height = blockid
    data = {
        "id":1, "jsonrpc":"2.0",
        "method":"eth_call",
        "params":[{"data": "0x"+function_hash(func_str)+args_str, "to": addr,}, height]
    }
    x = rpccall(endpoint, data)
    if os.environ.get("DEBUG", False):
        print()
    try:
        res = x.json()["result"]
    except:
        print(x, x.request.body, x.text)
        raise
    if not returnint:
        return res
    else:
        return int(res, 16)

def batch_callfunction(endpoint, datalist, height):
    data = []
    idx = -1
    if os.environ.get("DEBUG", False):
        print("[batch_call]", len(datalist), "calls")
    canfailidx = set()
    for item in datalist:
        idx += 1
        if len(item) == 3:
            addr, func_str, args_str = item
            extra = {}
        else:
            addr, func_str, args_str, extra = item
        if extra.get("canfail", False): #is this call possible to fail?
            canfailidx.add(idx)
        if func_str.startswith("eth_"):
            p = [args_str, height]
            if func_str == "eth_blockNumber":
                p = []
            if func_str=="eth_getBlockByNumber":
                p = [height, args_str]
            data.append({"id": idx, "jsonrpc":"2.0", "method":func_str,
                "params": p
            })
        else:
            data.append({"id": idx, "jsonrpc":"2.0", "method":"eth_call",
                "params":[{"data": "0x"+function_hash(func_str)+args_str, "to": addr,}, height]
            })
    if os.environ.get("DEBUG_VERBOSE", False):
        print(data)
        print(endpoint)
    x = rpccall(endpoint, data)
    if os.environ.get("DEBUG_VERBOSE", False):
        print(x.json())
    #print("canfailidx", canfailidx)
    try:
        resdata = x.json()
    except:
        print(x.text, x.url)
        raise
    res = []
    idx = -1
    for i in resdata:
        idx += 1
        try:
            res.append((i["id"],i["result"]))
        except:
            if idx in canfailidx:
                res.append((i["id"], None))
                continue
            print(i, x.url)
            if os.environ.get("ALLOW_FAIL", False):
                res.append((i["id"],i.get("result", None)))
                continue
            raise
    return res

def bd(result_str):
    # base64 decode rpc result str, return bytes
    if isinstance(result_str, tuple) and len(result_str)==2 and isinstance(result_str[0], int):
        result_str = result_str[1]
    if result_str.startswith("0x"):
        result_str = result_str[2:]
        if len(result_str)%2!=0:
            result_str = "0"+result_str
    return b16decode(result_str.upper())

def batch_callfunction_decode(endpoint, datalist, outtypes, height=None, needidx=False, batch_f=batch_callfunction, allow_decode_fail=False):
    """
    datalist: [contract_address, funcname(arg_type_list), encoded_arguments]
    outtypes: list of [return values' type list]
    Example:
        data = batch_callfunction_decode(H, [[addr, "symbol()", ""] for addr in addrs], [["string"]])
    Depends on eth_abi package
    """
    if not datalist:
        return []
    if isinstance(height, int):
        height = hex(height)
    elif not height:
        height = "latest"
    if not isinstance(outtypes[0], list):
        outtypes = [outtypes]*len(datalist)
    data = batch_f(endpoint, datalist, height)
    res = []
    for i, item in data:
        if not item:
            res.append((i, None))
        else:
            #print(outtypes[i], item)
            if outtypes[i]==["raw"]:
                d = item
            elif outtypes[i]==["hex"]:
                d = int(item, 16)
            elif outtypes[i]==["timestamp"]:
                d = int(item["timestamp"], 16)
            else:
                try:
                    d = eth_abi.decode_abi(outtypes[i], bd(item))
                except:
                    if allow_decode_fail or os.environ.get("ALLOW_DECODE_FAIL", False):
                        continue
                    else:
                        raise
                if len(d)==1:
                    d = d[0]
            res.append((i, d))
    if needidx:
        return res
    else:
        return [i[1] for i in res]

def batch_callRPC(data, retry=3, checkfunc=None, endpoint=None):
    assert endpoint is not None, "batch_callRPC need endpoint"
    x = None
    try:
        x = rpccall(endpoint, data)
        res = x.json()
        if checkfunc:
            checkfunc(res)
    except Exception as e:
        traceback.print_exc()
        if x:
            print(x.text, x)
        
        if retry:
            return batch_callRPC(data, retry=retry-1, checkfunc=checkfunc, endpoint=endpoint)
        else:
            raise
    return res

def batch_eth_getBlockByNumber(heights, endpoint=None, returnraw=False):
    data = []
    for height in heights:
        if isinstance(height, int):
            height = hex(height)
        data.append({"id":len(data),"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[height,True]})
    def f(res):
        assert res and isinstance(res, list), res
        assert "transactions" in res[0]["result"], res
    res = batch_callRPC(data, checkfunc=f, endpoint=endpoint)
    if returnraw:
        return res
    else:
        return [i["result"] for i in res]

def batch_eth_getTransactionANDReceipt(txids, endpoint=None):
    data = []
    for idx, txid in enumerate(txids):
        data.extend([{
            "id":1+idx*2, "jsonrpc":"2.0",
            "method":"eth_getTransactionByHash",
            "params":[txid]
        }, {
            "id":2+idx*2, "jsonrpc":"2.0",
            "method":"eth_getTransactionReceipt",
            "params":[txid]
        }, ])
    x = batch_callRPC(data, endpoint=endpoint)
    res = []
    for idx, txid in enumerate(txids):
        tx, receipt = x[idx*2:idx*2+2]
        tx = tx["result"]
        tx.update(receipt["result"])
        assert tx["hash"] == txid
        assert tx["transactionHash"] == txid
        res.append(tx)
    return res

FOLDER=os.path.abspath(os.path.dirname(__file__))

cache = {"bsc":None, "matic":None, "eth":None, "arb":None, "op":None, "avax":None}
class NoClosetBlock(Exception):
    pass
def scan_api_getblocknobytime(name, domain, date, ts, apikey):
    global cache
    if name not in cache or not cache[name]:
        try:
            cache[name] = json.load(open(f"{FOLDER}/ts2block600_{name}.json"))
        except:
            cache[name] = {}
    if date in cache[name]:
        return cache[name][date]
    url = f"{domain}/api?module=block&action=getblocknobytime&timestamp={ts}&closest=before&apikey={apikey}"
    if "://" not in url:
        url = "https://"+url
    #print(url)
    startts = time.time()
    try:
        x = sess.get(url)
        if "No closest block found" in x.text:
            raise NoClosetBlock(x)
        block = hex(int(x.json()["result"]))
        return block
    except:
        print(url)
        raise
    finally:
        elapsed = time.time()-startts
        if elapsed<0.25:
            sleep(0.25-elapsed)
    #print(date, block)
    

def loadts2block(name, domain, apikey, loaddays=90, period=86400, fmt="%Y/%m/%d"):
    f = f"{FOLDER}/ts2block{period}_{name}.json"
    try:
        ts2block = json.load(open(f))
    except Exception as e:
        print("error:", e)
        ts2block = {}
    changed=False
    totalrange = range(int(loaddays*86400/period))
    for idx, i in enumerate(totalrange):
        ts = int(time.time()//period-i)*period
        #print(i, ts)
        date = datetime.fromtimestamp(ts).strftime(fmt)
        if date in ts2block:
            continue
        if name=="matic" and 1646934856<ts< 1646950004:
            block = hex(25811391)
        else:
            try:
                block = scan_api_getblocknobytime(name, domain, date, ts, apikey)
            except NoClosetBlock:
                print("NoClosetBlock", name, date, ts)
                nextts = int(time.time()//period-totalrange[idx+1])*period
                nextdate = datetime.fromtimestamp(nextts).strftime(fmt)
                if nextdate in ts2block:
                    block=ts2block[nextdate]
                else:
                    continue
            except Exception as e:
                traceback.print_exc()
                continue
        ts2block[date] = block
        if int(100*idx/len(totalrange))%10==0:
            print(idx, "/", len(totalrange), date, block)
        changed=True
        if idx%10==0:
            open(f,"w").write(json.dumps(ts2block))
    if changed:
        open(f,"w").write(json.dumps(ts2block))
    return ts2block

def batch_callfunction_withblock(endpoint, datalist, height=None, timeout=50):
    #param height is ignored, passed by datalist
    data = []
    idx = -1
    if os.environ.get("DEBUG", False):
        print("[batch_call]", len(datalist), "calls")
    for addr, func_str, args_str, height_str in datalist:
        idx += 1
        if func_str.startswith("eth_"):
            params = [args_str, height_str]
            if func_str=="eth_getBlockByNumber":
                params = [height_str, args_str]
            data.append({"id": idx, "jsonrpc":"2.0", "method":func_str,
                "params": params
            })
        else:
            data.append({"id": idx, "jsonrpc":"2.0", "method":"eth_call",
                "params":[{"data": "0x"+function_hash(func_str)+args_str, "to": addr,}, height_str]
            })
    if os.environ.get("DEBUG_VERBOSE", False):
        print(data)
    x = rpccall(endpoint, data, timeout=timeout)
    if os.environ.get("DEBUG_VERBOSE", False):
        print(x.text)
        print(x.json())
    res = []
    if x.status_code!=200 or not isinstance(x.json(), list):
        print(x.text)
        raise Exception("rpc failed", endpoint)
    for i in x.json():
        if not i.get("result", None):
            print("error:", i)
        res.append((i["id"],i.get("result", None)))
    return res

def wrapper_init_check(f):
    def work_func(self, *args, **kwargs):
        if not self.init:
            self.update(self.getfunc())
            #print("Lazy Dict loaded")
        return f(self, *args, **kwargs)
    return work_func

class Lazy_Dict(dict):
    # this provides a dict object, but will load getfunc() data when being used
    def __init__(self, getfunc):
        self.init = False
        self.getfunc = getfunc
        for i in dir(dict):
            if i not in ["__class__", "__setattr__", "__getattr__", "__getattribute__", "update"] and callable(getattr(dict, i)):
                #print("hook method", i)
                setattr(self.__class__, i, wrapper_init_check(getattr(dict, i)))

CHAIN = os.environ.get("CHAIN", "bsc")
ts2block = None
if CHAIN=="matic":
    SCANDOMAIN, SCANKEY = "api.polygonscan.com", "1MGDR3B5H7DGA6575FK92CG9GNZH5G9SFM"
    nodes = CHAINRPCS["Polygon"]
    nodes_normal = [
        "https://rpc-mainnet.maticvigil.com/v1/9cdf203c46d3a7b7f1bdaa0a7e624133da091a8d",
        "https://matic-mainnet--jsonrpc.datahub.figment.io/?apikey=5688e5f9d801f1c1f8f64af205f0594a",
        "https://matic.mytokenpocket.vip",
        "https://rpc-mainnet.matic.quiknode.pro",
        "https://matic-mainnet-archive-rpc.bwarelabs.com",
    ]
elif CHAIN=="movr":
    SCANDOMAIN, SCANKEY = None, None
    nodes = CHAINRPCS["Moonriver"]
    def f_movr_ts2block():
        from chains.movr import movr_loadts2block
        return movr_loadts2block("movr")
    ts2block = Lazy_Dict(f_movr_ts2block)
    loadts2block = f_movr_ts2block
elif CHAIN=="eth":
    SCANDOMAIN, SCANKEY = "api.etherscan.io", "6XWIXGC71WS43NQSRIY7M87GAJMJJQ4UY8"
    nodes = CHAINRPCS["Ethereum"]
    nodes_normal = [
        "https://mainnet.infura.io/v3/98062ebb00754df2ae2911a2db0be28b",
        'https://mainnet.infura.io/v3/a1743f084f8a46bfb3696389eeb9f217',
        'https://mainnet.infura.io/v3/cad7f83b4e47462e90387487530239af',
        'https://mainnet.infura.io/v3/01e4876c179a49ebbf8ad09f7037d9ee',
        'https://mainnet.infura.io/v3/483c1730b99b46729c7f82f49302bbf8',
        'https://mainnet.infura.io/v3/fa3e2193dfcb48978f731fadf8a1282a',
        'https://mainnet.infura.io/v3/139b233124ca4a7cb78ac63cd0a2d29f',
        'https://mainnet.infura.io/v3/e846fc35019a4766babcc4e9e757bb74',
        'https://mainnet.infura.io/v3/b838cc16e73f482b960d1f86c05533a6',
        'https://mainnet.infura.io/v3/4ca56581b1234f2a9cf4b7333c1f8ac1',
        'https://mainnet.infura.io/v3/d266a83cc83a40d7b14257be4579d310',
    ]
elif CHAIN=="ftm":
    SCANDOMAIN, SCANKEY = "api.ftmscan.com", "QXNNTZRN4A4IXRAVMRGJVWZGRECMNZMB36"
    nodes = CHAINRPCS["Fantom"]
    nodes_normal = nodes
elif CHAIN=="arb":
    SCANDOMAIN, SCANKEY = "api.arbiscan.io", "T4W6BX6T2VRVTWNWD96A5A3DER8FUQ3M5S"
    nodes_normal = nodes = CHAINRPCS['Arbitrum']
elif CHAIN=="avax":
    SCANDOMAIN, SCANKEY = "api.snowtrace.io", "C99DRF9RV3HYS1M4QHCK4WX5EYUQ3QF8VU"
    nodes_normal = nodes = CHAINRPCS['Avalanche']
elif CHAIN=="op":
    SCANDOMAIN, SCANKEY = "api-optimistic.etherscan.io", "R3CW3DDS56NYJC33XBTGSRQCAN8IF8K9SH"
    nodes_normal = nodes = CHAINRPCS['Optimism']
elif CHAIN=="terra":
    nodes = [
        "https://columbus-5--lcd--archive.datahub.figment.io/apikey/a448a0ca115d1a8dd6bc700f9f6aa0e1/",
    ]
    nodes_normal = [
        "https://lcd.terra.dev/",
    ]
    def f_terra_ts2block():
        from chains.terra import terra_loadts2block
        return terra_loadts2block("terra")
    ts2block = Lazy_Dict(f_terra_ts2block)
else:
    CHAIN = "bsc"
    SCANDOMAIN, SCANKEY = "api.bscscan.com", "TMZVYEQS4ET8676VTB9SCK4XPQPTSXHCS2"
    nodes=CHAINRPCS["BSC"]
    nodes_normal = """https://apis.ankr.com/c0d871dd3c6d4529b01c9362a9b79e89/6106d4a3ec1d1bcc87ec72158f8fd089/binance/archive/main
https://proud-patient-forest.bsc.quiknode.pro/8fffb4d84f42ec02686c35631b566c819138e876/
https://patient-small-sound.bsc.quiknode.pro/e9d9c6fc165de5266e008da316e7b5220b1e1775/
https://ancient-snowy-moon.bsc.quiknode.pro/e4de697d846d1f1a152117267e5aed98d8977b2b/
https://bsc-private-dataseed1.nariox.org
https://bsc-private-dataseed2.nariox.org""".split("\n")

if ts2block is None:
    ts2block=Lazy_Dict(lambda:loadts2block(CHAIN, SCANDOMAIN, SCANKEY))

def simplecall(addr, func_str, result_handler, args_str = "", days=None, endpoint=None):
    items = sorted(ts2block.items())
    if days:
        items = items[-days:]
    if not endpoint:
        endpoint = nodes[0]
    print("use endpoint:", endpoint, file=sys.stderr)
    try:
        x=batch_callfunction_withblock(endpoint, [[addr, func_str, args_str, block] for ts,block in items])
    except:
        x=batch_callfunction_withblock(endpoint, [[addr, func_str, args_str, block] for ts,block in items])
    if os.environ.get("DEBUG", False):
        print(x)
    res = dict(zip([i[0] for i in items], [result_handler(i[1]) if i[1]!="0x" else 0 for i in x]))
    for date, nav in sorted(res.items()):
        if nav>0:
            print(date, nav, sep="\t")
    return res

@lru_cache()
def eth_getBlockByNumber(height, endpoint, needtx=True):
    if isinstance(height, int):
        height = hex(height)
    res = {}
    x = None
    try:
        x = rpccall(endpoint, {"id":6,"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[height,needtx]})
        if os.environ.get("DEBUG_VERBOSE", False):
            print(endpoint, x, x.text, height)
        res = x.json()["result"]
    except:
        if os.environ.get("DEBUG", False):
            if x:
                print(x, x.text, endpoint)
            traceback.print_exc()
        pass
    if not res or "transactions" not in res:
        if x:
            raise NoBlock(x.text)
        else:
            raise NoBlock("network failed, no x")
    return res

def eth_latestBlock(endpoint):
    x1 = rpccall(endpoint, {"id":1,"jsonrpc":"2.0","method":"eth_blockNumber","params":[]})
    x2 = rpccall(endpoint, {"id":2,"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",False]})
    if os.environ.get("DEBUG_VERBOSE", False):
        print(x1.text)
        print(x2.text)
    try:
        x1, x2 = x1.json(), x2.json()
    except:
        print(x1.text)
        print(x2.text)
        raise
    #print(int(x1["result"],16), int(x2["result"]["number"],16))
    if x1["result"]<=x2["result"]["number"]:
        return x2["result"]
    x = rpccall(endpoint, {"id":3,"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":[x1["result"],False]})
    return x.json()["result"]

def eth_latestTS(endpoint):
    latest = eth_latestBlock(endpoint)
    return toint(latest["number"]), toint(latest["timestamp"])

def eth_gasPrice(endpoint):
    x = rpccall(endpoint, {"id":1,"jsonrpc":"2.0","method":"eth_gasPrice","params":[]})
    return toint(x.json()["result"])

def retry_wrapper(f):
    def do_f(*args, **kwargs):
        global E
        j = 0
        for n in nodes:
            j += 1
            try:
                return f(*args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                print("error:", e, "retry:", i, "node:", j)
                E = n
                kwargs["endpoint"] = n
        return f(*args, **kwargs)
    return do_f

def Endpoint_Provider_retry_wrapper_allowexc(allowed_exceptions=None):
    def Endpoint_Provider_retry_wrapper(f):
        def do_f(self, *args, **kwargs):
            retrytimes = kwargs.get("retrytimes", 3)
            for i in range(retrytimes):
                j = 0
                for n in self.endpoints:
                    #print("about to try",n)
                    self.E = n
                    j += 1
                    try:
                        return f(self, *args, **kwargs)
                    except Exception as e:
                        if allowed_exceptions:
                            if any([isinstance(e, i) for i in allowed_exceptions]):
                                raise
                        traceback.print_exc()
                        print("error:", e, "retry:", i, "bad_node:", n)
                        self.endpoints = self.endpoints[1:]+[self.endpoints[0]]
                print("all failed, sleep 5")
                sleep(5)
        return do_f
    return Endpoint_Provider_retry_wrapper

Endpoint_Provider_retry_wrapper=Endpoint_Provider_retry_wrapper_allowexc()

class Endpoint_Provider():
    def __init__(self, endpoints):
        self.endpoints = endpoints
        self.E = endpoints[0]
    @Endpoint_Provider_retry_wrapper
    def callfunction(self, *args, **kwargs):
        #print("self.E", self.E)
        return callfunction(self.E, *args, **kwargs)
    @Endpoint_Provider_retry_wrapper
    def batch_callfunction_decode(self, *args, **kwargs):
        #print("self.E", self.E)
        return batch_callfunction_decode(self.E, *args, **kwargs)
    @Endpoint_Provider_retry_wrapper
    def erc20_balanceOf(self, *args, **kwargs):
        return erc20_balanceOf(self.E, *args, **kwargs)
    @Endpoint_Provider_retry_wrapper
    def eth_balanceOf(self, *args, **kwargs):
        return eth_balanceOf(self.E, *args, **kwargs)
    @Endpoint_Provider_retry_wrapper
    def eth_getTransactionANDReceipt(self, txid):
        return eth_getTransactionANDReceipt(self.E, txid)
    @Endpoint_Provider_retry_wrapper_allowexc([NoBlock])
    def eth_getBlockByNumber(self, height, needtx=True):
        return eth_getBlockByNumber(height, self.E, needtx=needtx)
    @Endpoint_Provider_retry_wrapper
    def eth_latestBlock(self):
        return eth_latestBlock(self.E)
    @Endpoint_Provider_retry_wrapper
    def eth_gasPrice(self):
        return eth_gasPrice(self.E)

class class_LP(Endpoint_Provider):
    def __init__(self, endpoints, contract, decimals=None, token0_name=None, token0_decimals=None, token1_name=None, token1_decimals=None):
        super().__init__(endpoints)
        self.contract = contract
        if not decimals:
            token0_addr, token1_addr = self.batch_callfunction_decode([[contract, "token0()", ""], [contract, "token1()", ""], ], ["address"])
            token0_name, token0_decimals, token1_name, token1_decimals, decimals = self.batch_callfunction_decode([
                [token0_addr, "symbol()", ""], [token0_addr, "decimals()", ""], 
                [token1_addr, "symbol()", ""], [token1_addr, "decimals()", ""], 
                [contract, "decimals()", ""]
            ], [["string"], ["uint256"], ["string"], ["uint256"], ["uint256"]])
            print(f"""class_LP(nodes, "{contract}", {decimals}, "{token0_name}", {token0_decimals}, "{token1_name}", {token1_decimals})""")
        self.decimals = decimals
        self.token0_name, self.token0_decimals = token0_name, token0_decimals
        self.token1_name, self.token1_decimals = token1_name, token1_decimals
        
    def fetch_history(self, heights, div_decimals=True):
        data = []
        types = []
        for h in heights:
            if isinstance(h, int):
                h = hex(h)
            data.append([self.contract, "getReserves()", "", h])
            types.append(["uint256","uint256","uint256"])
            data.append([self.contract, "totalSupply()", "", h])
            types.append(["uint256"])
        x = self.batch_callfunction_decode(data, types, batch_f=batch_callfunction_withblock, allow_decode_fail=True)
        res = []
        for i, h in enumerate(heights):
            if isinstance(h, str):
                h = int(h, 16)
            try:
                (r0, r1, _), totalsupply = x[i*2:(i+1)*2]
            except:
                break
            if div_decimals:
                res.append([h, r0/10**self.token0_decimals, r1/10**self.token1_decimals, totalsupply/10**self.decimals])
            else:
                res.append([h, r0, r1, totalsupply])
        return res
    
    def updatetodb(self, tablename, ts2block, decimals_conf, startts=None):
        from runsql import runsql
        # decimals_conf = [6, 6, 10], means save to db (r0*1e6, r1*1e6, totalsupply*1e10)
        allts = [int(i) for i in ts2block.keys()]
        mints = min(allts)
        if startts:
            mints = max(mints, startts)
        runsql(f"create table if not exists {tablename} like template_lp")
        known = set([int(i[0]) for i in runsql(f"select ts from {tablename} where ts>={mints}")])
        sqlhead = f"replace into {tablename}(ts,block,reserve0,reserve1,totalsupply) values"
        items = [i for i in sorted(ts2block.items(), reverse=True) if int(i[0]) not in known and int(i[0])>=mints]
        print(tablename, "len(known)=",len(known), "len(items)=",len(items))
        BATCH_SIZE = 100
        for i in range(0,len(items),BATCH_SIZE):
            sql = sqlhead
            pending = []
            tss = [i[0] for i in items[i:i+BATCH_SIZE]]
            heights = [i[1] for i in items[i:i+BATCH_SIZE]]
            x = self.fetch_history(heights)
            isfirst = True
            for ts, (h, r0, r1, totalsupply) in zip(tss,x):
                store_r0, store_r1, store_totalsupply = r0*10**decimals_conf[0], r1*10**decimals_conf[1], totalsupply*10**decimals_conf[2]
                if isfirst:
                    print(ts, h, store_r0, store_r1, store_totalsupply)
                    isfirst = False
                sql += "(%s"+",%s"*(5-1)+"),"
                pending.extend([ts, h, store_r0, store_r1, store_totalsupply])
            if pending:
                runsql(sql, pending)
            else:
                print("no data", items[i])
                break

class TokenPrice(Endpoint_Provider):
    def __init__(self, endpoints, router, intokendecimals, outtokendecimals, paths):
        super().__init__(endpoints)
        self.router = router
        self.intokendecimals = intokendecimals
        self.outtokendecimals = outtokendecimals
        self.paths = paths
    def getprice(self, heights, amount):
        data = []
        types = []
        for h in heights:
            if isinstance(h, int):
                h = hex(h)
            for path in self.paths:
                itemdata = b16encode(eth_abi.encode_abi(["uint256","address[]"], [amount*10**self.intokendecimals, path])).decode().lower()
                data.append([self.router, "getAmountsOut(uint256,address[])", itemdata, h])
                types.append(["uint256[]"])
        x = self.batch_callfunction_decode(data, types, batch_f=batch_callfunction_withblock)
        N = len(self.paths)
        res = []
        for i, h in enumerate(heights):
            pathres = x[i*N:(i+1)*N]
            print(pathres)
            bestoutput = sorted(pathres, key=lambda item:item[-1], reverse=True)[0]
            res.append(bestoutput[-1]/10**self.outtokendecimals/ amount)
        return res


E=nodes[int(os.environ.get("E", 0))]
#print("using rpc:", E)

def binary_search(low, high, func):
    mid = 0
    while low <= high:
        mid = int((high + low) // 2)
        r = func(mid)
        if r<0:
            low = mid + 1
        elif r>0:
            high = mid - 1
        else:
            return mid
    return mid#raise Exception("cannot binary search")

def toint(h):
    return int(h, 16)

class class_TS2BLOCK_RPC():
    def __init__(self, name, endpoint, f_block2ts, f_latest):
        self.name = name
        self.f_block2ts = f_block2ts
        self.f_latest = f_latest
        self.endpoint = endpoint
        self.ts2block = None
        self.latest_height, self.latest_ts = None, None
        self.global_refnumber, self.global_refts = None, None

    def func_ts2block(self, ts, retry=3):
        endpoint = self.endpoint
        block2ts = self.f_block2ts
        if not self.global_refnumber:
            self.latest_height, self.latest_ts = self.f_latest(endpoint=endpoint)
            self.global_refnumber = self.latest_height
            self.global_refts = self.latest_ts
            print("latest:", self.latest_height, "->", self.latest_ts)
        if not cache.get(self.name): #cache from base.py
            cache[self.name] = json.load(open(f"{FOLDER}/ts2block600_{self.name}.json"))
        if str(ts) in cache[self.name]:
            return cache[self.name][str(ts)]
        
        assert ts<=self.latest_ts
        refnumber, refts = self.global_refnumber, self.global_refts
        speed = (refts - block2ts(refnumber-100)) / 100
        guess = refnumber
        diff_ts = refts - ts
        #print("diff:", diff_ts)
        iter_cnt = 0
        while abs(diff_ts)>abs(speed)*2 and iter_cnt<10:
            iter_cnt += 1
            diff_blockcnt = int(diff_ts/speed)
            if diff_blockcnt==0:
                break
            guess = refnumber-diff_blockcnt
            if guess>self.latest_height:
                break
            if guess<0:
                #guess = min(ts2block.values())
                #continue
                refnumber = random.randint(100, min(ts2block.values()))
                #refnumber = min(ts2block.values())
                refts = block2ts(refnumber, endpoint=endpoint)
                n = random.randint(10, 100)
                speed = (refts - block2ts(refnumber-n)) / n
                guess = refnumber
                diff_ts = refts - ts
                continue
            if os.getenv("DEBUG"):
                print("diff:", diff_ts, "guess:", guess, "speed:", speed)
            newblockts = block2ts(guess, endpoint=endpoint)#eth_getBlockByNumber(guess, endpoint=endpoint)
            if refts != newblockts and diff_blockcnt>10:
                speed = (refts - newblockts) / diff_blockcnt
            refnumber = guess
            refts = newblockts
            diff_ts = newblockts - ts
        
        if abs(diff_ts) > 1000:
        #    raise Exception("failed search")
            assert block2ts(100)<ts
            while block2ts(guess)<ts:
                guess = random.randint(guess, self.latest_height)
            assert block2ts(guess)>=ts
            def f_search(i):
                diff = block2ts(i)-ts
                #print(i, "diff:", diff)
                return diff
            guess = binary_search(100, guess, f_search)
        while block2ts(guess, endpoint=endpoint)>ts:
            guess -= 1
        guess += 1
        while block2ts(guess, endpoint=endpoint)<=ts:
            guess += 1
        self.global_refnumber, self.global_refts = refnumber, refts
        return guess-1

    def loadts2block(self, name, loaddays=90, period=86400, fmt="%Y/%m/%d"):
        ts2block = self.ts2block
        f = f"{FOLDER}/ts2block{period}_{name}.json"
        try:
            ts2block = json.load(open(f))
        except:
            ts2block = {}
        changed=0
        missing_len = len([i for i in range(int(loaddays*86400/period)) if (str if fmt=="%s" else lambda ts:datetime.fromtimestamp(ts).strftime(fmt))(int(time.time()//period-i)*period) not in ts2block])
        if missing_len:
            print("missing:", missing_len)
        for i in range(int(loaddays*86400/period)):
            ts = int(time.time()//period-i)*period
            if fmt=="%s":
                date = str(ts)
            else:
                date = datetime.fromtimestamp(ts).strftime(fmt)
            if date in ts2block:
                continue
            if os.getenv("DEBUG"):
                print(i, ts)
            try:
                block = self.func_ts2block(ts)
            except Exception as e:
                traceback.print_exc()
                print("[func_ts2block] failed, writing cache")
                break
            ts2block[date] = block
            changed+=1
            if changed%10==0:
                open(f,"w").write(json.dumps(ts2block))
        if changed:
            open(f,"w").write(json.dumps(ts2block))
        return ts2block

def erc20_balanceOf(endpoint, contract, addr):
    return callfunction(endpoint, contract, "balanceOf(address)", toarg(addr))

def eth_balanceOf(endpoint, addr):
    return int(batch_callfunction(endpoint, [["", "eth_getBalance", addr]], "latest")[0][1], 16)

def eth_getTransactionANDReceipt(endpoint, txid):
    data = [{
        "id":1, "jsonrpc":"2.0",
        "method":"eth_getTransactionByHash",
        "params":[txid]
    }, {
        "id":2, "jsonrpc":"2.0",
        "method":"eth_getTransactionReceipt",
        "params":[txid]
    }, ]
    x = rpccall(endpoint, data)
    assert x.status_code == 200, x.text
    if os.environ.get("DEBUG_VERBOSE"):
        print(x.text)
    tx, receipt = x.json()
    tx = tx["result"]
    tx.update(receipt["result"])
    return tx

def D(i, j=None):
    if j:
        return Decimal(int(i, j))
    else:
        return Decimal(i)

@lru_cache()
def get_anyswap_chaininfo():
    return sess.get("https://bridgeapi.anyswap.exchange/data/bridgeChainInfo").json()

def chainid2name(chainid):
    chainid = str(chainid)
    if chainid not in _chainid2name:
        anyswap_chaininfo = get_anyswap_chaininfo()
        if chainid in anyswap_chaininfo:
            return anyswap_chaininfo[chainid]["name"]
    return _chainid2name.get(chainid, chainid)

def chainname2id(name):
    return int(_chainname2id[name])

def ensure_chainname(f):
    def wrapped(chainname):
        if isinstance(chainname, int) or chainname.isdigit():
            chainname = chainid2name(chainname)
        return f(chainname)
    return wrapped

CHAINLIST = None

@ensure_chainname
def chain2rpcs(chainname):
    global CHAINLIST
    rpcs = CHAINRPCS.get(chainname, None)
    if not rpcs:
        if not CHAINLIST:
            CHAINLIST = {i["chainId"]:i for i in sess.get("https://chainid.network/chains.json").json()}
        c = chainname.lower()
        for chainid, item in CHAINLIST.items():
            if "testnet" in item["name"].lower():
                continue
            if c==item["name"].lower() or c==item["chain"].lower():
                return [i for i in item["rpc"] if i.startswith("http")]
        for chainid, item in get_anyswap_chaininfo().items():
            if c==chainid or c==item["name"].lower():
                return [item["rpc"]]
    return rpcs

def chain2provider(chainname):
    rpcs = chain2rpcs(chainname)
    assert rpcs is not None, "no such chain "+chainname
    return Endpoint_Provider(rpcs)

@ensure_chainname
def chain2scandomain(chainname):
    return CHAINSCAN.get(chainname, None)

@ensure_chainname
def chain2nativetoken(chainname):
    return CHAINNATIVE.get(chainname, None)

CHAIN2WETH = {i:j.lower() for i,j in {
    "Ethereum":  "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "BSC": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    "Polygon": "0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270",
    "Fantom": "0x21be370d5312f44cb42ce377bc9b8a0cef1a4c83",
    "Moonriver": "0x98878B06940aE243284CA214f92Bb71a2b032B8A",
    "Avalanche": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
    "Harmony": "0xcf664087a5bb0237a0bad6742852ec6c8d69a27a",
    "Arbitrum": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
}.items()}

@ensure_chainname
def chain2weth(chainname):
    return CHAIN2WETH.get(chainname, None)

import threading
thread_data = threading.local()
def getsess():
    sess = thread_data.__dict__.get("sess")
    if not sess:
        sess=requests.session()
        sess.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"})
        thread_data.__dict__["sess"] = sess
    return sess

Arb="https://arb1.arbitrum.io/rpc"

def eth_getStorageAt(endpoint, contract, index, height="latest", format="int"):
    if isinstance(index, int):
        index = hex(index)
    if isinstance(height, int):
        height = hex(height)
    data = {
        "id":1, "jsonrpc":"2.0",
        "method":"eth_getStorageAt",
        "params":[contract, index, height]
    }
    x = rpccall(endpoint, data)
    shouldprint = os.environ.get("DEBUG", False)
    err = None
    try:
        res = x.json()["result"]
    except Exception as e:
        err = e
        shouldprint = True
    if shouldprint:
        print(x, x.text)
    if err:
        raise err
    if format == "int":
        return int(res, 16)
    elif format == "addr":
        return "0x"+res[-40:]
    else:
        return res

_IMPLEMENTATION_SLOT = 0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc
def getImpl(endpoint, address):
    return eth_getStorageAt(endpoint, address, _IMPLEMENTATION_SLOT, "latest", "addr")
