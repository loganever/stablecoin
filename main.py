from web3 import Web3
from web3 import HTTPProvider
import requests
import json
import time
import copy
import time
from base import loadts2block
from datetime import date
import pymysql
import csv
import xlwt


# def insert(data):
#     db = pymysql.connect(
#         host="", 
#         port=,
#         user='root',
#         password='',
#         database='stable',
#         charset='utf8mb4' 
#         )
#     cursor = db.cursor()
#     sql = "insert into coin(chain,contract_address,date,coin_list,balance_list,ratio_list) values"
#     for i in data:
#         sql+="('%s','%s','%s','%s','%s','%s')," % (i[0],i[1].lower(),i[2],i[3],i[4],i[5])
#     cursor.execute(sql[:-1])
#     conn.commit()
#     conn.close()


def get_balance(pool):
    pool = Web3.toChecksumAddress(pool)
    web3 = Web3(HTTPProvider(provider))
    abi='[{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'
    usdc_address = Web3.toChecksumAddress('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')
    usdt_address = Web3.toChecksumAddress('0xdac17f958d2ee523a2206206994597c13d831ec7')
    dai_address = Web3.toChecksumAddress('0x6b175474e89094c44da98b954eedeac495271d0f')
    busd_address = Web3.toChecksumAddress('0x4Fabb145d64652a948d72533023f6E7A623C7C53')
    dai_usdc_usdt_3crv_address = Web3.toChecksumAddress('0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490')
    usdc_contract_instance = web3.eth.contract(address=usdc_address, abi=abi)
    usdt_contract_instance = web3.eth.contract(address=usdt_address, abi=abi)
    dai_contract_instance = web3.eth.contract(address=dai_address, abi=abi)
    busd_contract_instance = web3.eth.contract(address=busd_address, abi=abi)
    dai_usdc_usdt_3crv_contract_instance = web3.eth.contract(address=dai_usdc_usdt_3crv_address, abi=abi)
    dai = []
    usdc = []
    usdt = []
    busd = []
    dai_usdc_usdt_3crv = []
    for key in num.keys():
        #print(key)
        block = int(num[key],16)
        dai_num = dai_contract_instance.functions.balanceOf(pool).call(block_identifier=block) / 1e18
        usdc_num = usdc_contract_instance.functions.balanceOf(pool).call(block_identifier=block) / 1e6
        usdt_num = usdt_contract_instance.functions.balanceOf(pool).call(block_identifier=block) / 1e6
        busd_num = busd_contract_instance.functions.balanceOf(pool).call(block_identifier=block) / 1e18
        dai_usdc_usdt_3crv_num = dai_usdc_usdt_3crv_contract_instance.functions.balanceOf(pool).call(block_identifier=block) / 1e18
        dai.append(float(dai_num))
        usdc.append(float(usdc_num))
        usdt.append(float(usdt_num))
        busd.append(float(busd_num))
        dai_usdc_usdt_3crv.append(float(dai_usdc_usdt_3crv_num))
    result = []
    return {"DAI":dai,"USDC":usdc,"USDT":usdt,"BUSD":busd,"DAI/USDC/USDT(3CRV)":dai_usdc_usdt_3crv}

# config
provider = 'http://rpc'
pool_names = ['Curve 3pool','Curve busdv2','Uni DAI-USDC-0.01%','Uni DAI-USDC-0.05%','Uni USDC-USDT-0.01%','Uni USDC-USDT-0.05%','Uni BUSD-USDC-0.05%','Uni BUSD-USDC-0.01%']
pool_addresses = ['0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7','0x4807862aa8b2bf68830e4c8dc86d0e9a998e085a','0x5777d92f208679db4b9778590fa3cab3ac9e2168','0x6c6bc977e13df9b0de53b251522280bb72383700','0x3416cf6c708da44db2624d63ea0aaef7113527c6','0x7858e59e0c01ea06df3af3d20ac7b0003275d4bf','0x00cef0386ed94d738c8f8a74e8bfd0376926d24c','0x5e35c4eba72470ee1177dcb14dddf4d9e6d915f4']
coin_names = [['DAI','USDC','USDT'],['BUSD','DAI/USDC/USDT(3CRV)'],['DAI','USDC'],['DAI','USDC'],['USDC','USDT'],['USDC','USDT'],['BUSD','USDC'],['BUSD','USDC']]

num = loadts2block("eth","api.etherscan.io","WFBW6NI9Q4E5RSE15TH3UFPJ73PVPYDD8W",loaddays=92)

all_data = []
for k in range(len(pool_addresses)):
    pool_address = pool_addresses[k]
    pool_name = pool_names[k]
    coin_name = coin_names[k]
    coin = get_balance(pool_address)

    data = []
    i = 0
    for key in num.keys():
        sum = 0
        for name in coin_name:
            sum+=coin[name][i]
        temp = [key]
        for name in coin_name:
            temp.append(int(coin[name][i]))
            temp.append(round(coin[name][i]/sum,4))
        data.append(temp)
        i+=1
    all_data.append(data)

wb = xlwt.Workbook()
for k in range(len(pool_addresses)):
    data = all_data[k]
    pool_address = pool_addresses[k]
    pool_name = pool_names[k]
    coin_name = coin_names[k]
    ws = wb.add_sheet(pool_name, cell_overwrite_ok=True)
    ws.write(0, 0, "Date")
    for i in range(len(coin_name)):
        ws.write(0, 2*i+1, coin_name[i]+" Balance")
        ws.write(0, 2*i+2, coin_name[i]+" Ratio")
    for i in range(len(data)):
        ws.write(i + 1, 0, str(data[i][0]))
        for j in range(len(coin_name)):
            ws.write(i + 1, 2*j+1, str(data[i][2*j+1]))
            ws.write(i + 1, 2*j+2, str(data[i][2*j+2]))
wb.save('result.xls')
