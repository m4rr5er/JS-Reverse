from fontTools.ttLib import TTFont
import ddddocr
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def convert_cmap_to_image(cmap_code, font_path):
    img_size = 1024
    # 准备三要素：image画布  draw画笔 font字体
    img = Image.new("1", (img_size, img_size), 255)  # 创建一个黑白图像对象
    draw = ImageDraw.Draw(img)  # 创建绘图对象
    # 如果识别不准，如果是因为字体太大了，可以将img_size调成 int(img_size * 0.7)之类的
    font = ImageFont.truetype(font_path, img_size)  # 加载字体文件

    # 将 cmap code 转换为字符
    character = chr(cmap_code)
    # print("character:",character)
    bbox = draw.textbbox((0, 0), character, font=font)  # 获取文本在图像中的边界框
    width = bbox[2] - bbox[0]  # 文本的宽度
    height = bbox[3] - bbox[1]  # 文本的高度
    # 如果图片中文字靠下，可以调为(img_size - height) // 7 左右
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
        # print("text:", text)
        # image.save(f"./imgs/{text}.png", "PNG")  # 保存图像

        # print(f"Unicode码点：{cmap_code} - Unicode字符:{glyph_name}，识别结果：{text}")
        font_map[cmap_code] = text

    return font_map


font_file_path = "font.woff"
print(extract_text_from_font(font_file_path))
