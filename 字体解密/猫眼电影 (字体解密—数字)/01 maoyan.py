import requests
import re
from fontTools.ttLib import TTFont
import ddddocr
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from lxml import etree


cookies = {
    '__mta': '141882637.1719377969700.1719378227484.1720862981357.7',
    'uuid_n_v': 'v1',
    'uuid': 'DDBE40E0337811EFB68E812F46251267C957ACAF4AFB4C57AA50A05CE0737D88',
    '_csrf': 'ec509db4813923e1fd67580c732c5af8af46b2c39b74aa8206b21674c8ded952',
    'Hm_lvt_703e94591e87be68cc8da0da7cbd0be2': '1719377969',
    '_lxsdk_cuid': '19052e9bdf7c8-0c0b857db77fe8-1a525637-1612e8-19052e9bdf7c8',
    '_lxsdk': 'DDBE40E0337811EFB68E812F46251267C957ACAF4AFB4C57AA50A05CE0737D88',
    'HMACCOUNT': '790074E38A99D887',
    'Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2': '1720872730',
    '__mta': '141882637.1719377969700.1720862981357.1720872730686.8',
    '_lxsdk_s': '190abe8fb66-1b3-17-d89%7C%7C12',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    # 'Cookie': '__mta=141882637.1719377969700.1719378227484.1720862981357.7; uuid_n_v=v1; uuid=DDBE40E0337811EFB68E812F46251267C957ACAF4AFB4C57AA50A05CE0737D88; _csrf=ec509db4813923e1fd67580c732c5af8af46b2c39b74aa8206b21674c8ded952; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1719377969; _lxsdk_cuid=19052e9bdf7c8-0c0b857db77fe8-1a525637-1612e8-19052e9bdf7c8; _lxsdk=DDBE40E0337811EFB68E812F46251267C957ACAF4AFB4C57AA50A05CE0737D88; HMACCOUNT=790074E38A99D887; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1720872730; __mta=141882637.1719377969700.1720862981357.1720872730686.8; _lxsdk_s=190abe8fb66-1b3-17-d89%7C%7C12',
    'Pragma': 'no-cache',
    'Referer': 'https://www.maoyan.com/films',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}

params = {
    'showType': '2',
}

response = requests.get('https://www.maoyan.com/films', params=params, cookies=cookies, headers=headers)
data = response.text

# (1) 下载woff文件
path = re.findall(',url\("(.*?woff)"', response.text)[0]
print(path)
woff_url = "https:" + path

res = requests.get(woff_url)

with open("font.woff", "wb") as f:
    f.write(res.content)


# (2) 提取字体映射函数

def convert_cmap_to_image(cmap_code, font_path):
    img_size = 1024
    # 准备三要素：image画布  draw画笔 font字体
    img = Image.new("1", (img_size, img_size), 255)  # 创建一个黑白图像对象
    draw = ImageDraw.Draw(img)  # 创建绘图对象
    font = ImageFont.truetype(font_path, img_size)  # 加载字体文件

    # 将 cmap code 转换为字符
    character = chr(cmap_code)
    # print("character:",character)
    bbox = draw.textbbox((0, 0), character, font=font)  # 获取文本在图像中的边界框
    width = bbox[2] - bbox[0]  # 文本的宽度
    height = bbox[3] - bbox[1]  # 文本的高度
    draw.text(((img_size - width) // 2, (img_size - height) // 2), character, font=font)  # 绘制文本，并居中显示
    return img


def extract_text_from_font(font_path):
    font = TTFont(font_path)  # 加载字体文件
    # font.saveXML("xxx.xml")
    # 图像识别的模块：DdddOcr
    ocr = ddddocr.DdddOcr(beta=True, show_ad=False)  # 实例化 ddddocr 对象

    # print("font.getBestCmap().items():", font.getBestCmap().items())

    font_map = {}
    for cmap_code, glyph_name in font.getBestCmap().items():
        image = convert_cmap_to_image(cmap_code, font_path)  # 将字体字符转换为图像

        # 提取图像字符
        bytes_io = BytesIO()
        image.save(bytes_io, "PNG")
        text = ocr.classification(bytes_io.getvalue())  # 图像识别
        print("text:", text)
        # image.save(f"./imgs/{text}.png", "PNG")  # 保存图像

        print(f"Unicode码点：{cmap_code} - Unicode字符:{glyph_name}，识别结果：{text}")
        font_map[glyph_name.replace("uni", "&#x").lower()] = text

    return font_map


font_map = extract_text_from_font("font.woff")
print("font_map:::", font_map)

# (3) 字体解密

for k, v in font_map.items():
    data = data.replace(k + ";", v)
print(data)


# (4) 解析数据
html_Data = etree.HTML(data)
div_list = html_Data.xpath('//dl[@class="movie-list"]//dd')

for v in div_list:
    try:
        title = v.xpath(f'./div[2]/a/text()')[0]
        stone_font = v.xpath(f'./div[3]/span/text()')[0]

        print("title:", title)
        print("stone_font:", stone_font)
        print("*" * 30)
    except IndexError:
        continue

