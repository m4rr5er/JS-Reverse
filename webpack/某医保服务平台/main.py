import requests
import json
import execjs

js_code = open("func.js").read()
js_compile = execjs.compile(js_code)

headers = {
    "Accept": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://fuwu.nhsa.gov.cn",
    "Referer": "https://fuwu.nhsa.gov.cn/nationalHallSt/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
    "X-Tingyun": "c=B|4Nl_NnGbjwY;x=53131a19833b403e",
    "channel": "web",
    "contentType": "application/x-www-form-urlencoded",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "x-tif-nonce": "f7Q5yArn",
    "x-tif-paasid": "undefined",
    "x-tif-signature": "46baf073bdf8808297a6f04acadfb736b1a9fa19b413d59468f8a132f2f6714e",
    "x-tif-timestamp": "1750315711"
}
cookies = {
    "gb_nthl_sessionId": "a62851a87b3e4e4f9d00f00190bb01c7",
    "acw_tc": "276aedce17503156915578687e2fc0bdc37dda0f7d6057dbefe23a79ec4db0",
    "amap_local": "510100",
    "yb_header_active": "-1"
}
url = "https://fuwu.nhsa.gov.cn/ebus/fuwu/api/nthl/api/CommQuery/queryRtalPhacBInfo"

pageNum = 1
json_data = js_compile.call("getRequestData", pageNum).get("data")
data = json.loads(json_data)
# print(data)

data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers, cookies=cookies, data=data)

# print(response.json())
result = js_compile.call("decryptData", response.json())
# print(result)
for i in result['list']:
    # print(i.get('medinsName'), i.get('addr'))
    print(f"药店名称：{i.get('medinsName')}，地址：{i.get('addr')}")