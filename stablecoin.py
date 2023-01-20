# -*- codeing = utf-8 -*-
from web3 import Web3
from web3 import HTTPProvider
import time
from base import loadts2block
import config
import threading


class Swap:

    def __init__(self):
        self.web3 = [Web3(HTTPProvider(config.filter_provider[i]))  for i in range(len(config.filter_provider))]
        self.index = 0
        self.fliters = []
        self.now_block = self.web3[self.index%len(self.web3)].eth.blockNumber - 4*60*4
        for i in range(len(config.pool_names)):
            host = config.pool_names[i].split(" ")[0]
            topic = config.swap_event_topic[host]
            address = config.pool_addresses[i]
            self.fliters.append({"address":Web3.toChecksumAddress(address),"name":config.pool_names[i],"topic":topic,"host":host,"coins":config.coin_names[i]})
        self.data = {}
        thread = threading.Thread(target=self.run)
        thread.start()

    def run(self):
        while True:
            try:
                self.index+=1
                new_block = self.web3[self.index%len(self.web3)].eth.blockNumber
                if new_block - self.now_block >= 1:
                    for i in range(self.now_block+1,new_block+1):
                        self.data[i] = []
                    for i in self.fliters:
                        filter = self.web3[self.index%len(self.web3)].eth.filter({
                            "fromBlock": self.now_block+1,
                            "toBlock": new_block,
                            "address": i['address'],
                            "topics": [
                                i['topic']
                            ]
                        })
                        log_entries = filter.get_all_entries()
                        for j in log_entries:
                            block = j['blockNumber']
                            timestamp = self.web3[self.index%len(self.web3)].eth.getBlock(int(block)).timestamp
                            hash = j['transactionHash'].hex()
                            address = j['address']
                            topics = j['topics']
                            event_data = j['data']
                            split_event_data = []
                            index = 2
                            while index<len(event_data):
                                split_event_data.append(event_data[index:index+64])
                                index+=64
                            for k in range(len(topics)):
                                topics[k] = topics[k].hex()
                            if i['host']=='Curve':
                                volume = int(split_event_data[1],16)/config.coin[i['coins'][int(split_event_data[0],16)]]['decimal']
                                if volume>config.threshhold:
                                    self.data[block].append({"timestamp":timestamp,"swapFrom":i['coins'][int(split_event_data[0],16)],'swapTo':i['coins'][int(split_event_data[2],16)],'volume':volume,'transcationHash':hash,'pool_address':address,"pool_name":i['name']})
                            elif i['host']=='Uni':
                                if int(split_event_data[1],16) > 0 and int(split_event_data[1],16) < 1e50:
                                    volume = int(split_event_data[1],16)/config.coin[i['coins'][1]]['decimal']
                                    if volume>config.threshhold:
                                        self.data[block].append({"timestamp":timestamp,"swapFrom":i['coins'][1],'swapTo':i['coins'][0],'volume':volume,'transcationHash':hash,'pool_address':address,"pool_name":i['name']})
                                else:
                                    volume = int(split_event_data[0],16)/config.coin[i['coins'][0]]['decimal']
                                    if volume>config.threshhold:
                                        self.data[block].append({"timestamp":timestamp,"swapFrom":i['coins'][0],'swapTo':i['coins'][1],'volume':volume,'transcationHash':hash,'pool_address':address,"pool_name":i['name']})                 
                    self.now_block = new_block
            except Exception as e:
                print(e)
            time.sleep(15)


class StableCoinRatio:

    def __init__(self):
        self.web3 = Web3(HTTPProvider(config.provider))
        self.data_time = time.time()
        self.data = {}
        self.num = {}
        self.get_stable_coin_ratio()

    def get_data(self):
        if time.time()-self.data_time>config.cache_time:
            self.data_time = time.time()
            thread = threading.Thread(target=self.get_stable_coin_ratio)
            thread.start()
        return self.data

    def get_stable_coin_ratio(self):
        num = loadts2block("eth","api.etherscan.io",config.APIKEY,loaddays=config.history_days)
        self.num = num
        data = {}
        for k in range(len(config.pool_addresses)):
            pool_address = config.pool_addresses[k]
            pool_name = config.pool_names[k]
            coin_name = config.coin_names[k]
            coin = self.get_pool_data(pool_address)
            data[pool_name] = {}
            for name in coin_name:
                data[pool_name][name] = {}
            i = 0
            for key in num.keys():
                sum = 0
                for name in coin_name:
                    sum+=coin[name][i]
                for name in coin_name:
                    data[pool_name][name][key] = {"balance":int(coin[name][i]),"ratio":round(coin[name][i]/sum,4)}
                i+=1
            # for name in coin_name:
            #     data[pool_name][name] = sorted(data[pool_name][name].items(),key=lambda s:s[0])
        self.data = data

    def get_pool_data(self,pool):
        pool = Web3.toChecksumAddress(pool)
        contract_instance = []
        data = {}
        for coin_name in config.coin.keys():
            contract_instance.append({"instance":self.web3.eth.contract(address=Web3.toChecksumAddress(config.coin[coin_name]['address']), abi=config.balance_abi),"decimal":config.coin[coin_name]['decimal'],"name":coin_name})
            data[coin_name] = []
        for key in self.num.keys():
            block = int(self.num[key],16)
            for i in contract_instance:
                coin_num = i['instance'].functions.balanceOf(pool).call(block_identifier=block) / i['decimal']
                data[i['name']].append(float(coin_num))
        return data

if __name__ == "__main__":
    Swap()