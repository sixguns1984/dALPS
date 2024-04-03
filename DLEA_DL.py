import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
import pandas as pd
import numpy as np
from PIL import Image
import torch
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import shutil


# 第一段代码 - 图片resize
def resize_images(input_dir, output_dir):
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        if os.path.isfile(file_path):
            img = Image.open(file_path)
            img = img.resize((224, 224), Image.LANCZOS)
            img.save(os.path.join(output_dir, file))

# 第二段代码 - 使用VGG16预测
def predict_with_vgg16(model_path,output_dir):
    os.environ['CUDA_VISIBLE_DEVICES'] = '1'
    model = load_model(model_path)
    filenames = os.listdir(output_dir)
    predictions = []
    for filename in filenames:
        img_path = os.path.join(output_dir, filename)
        img = load_img(img_path, target_size=(224, 224))
        img = img_to_array(img)
        img = img.reshape(1, 224, 224, 3)
        prob = model.predict(img)
        pred = np.round(prob)
        predictions.append((filename, prob, pred))
    predictions_df = pd.DataFrame(predictions, columns=['filename', 'probability', 'prediction'])
    predictions_df = predictions_df.replace('[', '').replace(']', '')
    return predictions_df

##################################################################################### 
# 设置输入输出目录
input_dir = '/public/labdata/lincha/alps/adni3/ADNI_1/png/'
output_dir = /home/lincha/tem5/adni/adni1/resized_png/'
vgg16_model_path = '/home/lincha/tem3/try3/threeblocks_train2.h5'
target_directory = '/home/lincha/tem5/adni/adni1/png_yes/' # 放yes_png的目录

os.makedirs(output_dir, exist_ok=True)
os.makedirs(target_directory, exist_ok=True)

# 第一段代码 - 图片resize
resize_images(input_dir, output_dir)

# 第二段代码 - 使用VGG16预测
vgg16_predictions_df = predict_with_vgg16(vgg16_model_path, output_dir)
vgg16_predictions_df.to_csv('predictions.csv')
with open('predictions.csv', 'r') as file:
    content = file.read()

cleaned_content = content.replace('[', '').replace(']', '')
with open('predictions_cleaned.csv', 'w') as file:
    file.write(cleaned_content)

os.remove('predictions.csv')
print("符号已经去除并保存到 predictions_cleaned.csv")

df = pd.read_csv('predictions_cleaned.csv')
# 遍历数据框中的行
for index, row in df.iterrows():
    filename = row['filename']  # 替换为实际的列名
    prediction = row['prediction']  # 替换为实际的列名
    if prediction == 1:
        source_file = os.path.join(input_dir, filename)
        target_file = os.path.join(target_directory, filename)
        # 复制文件到目标目录
        shutil.copy(source_file, target_file)
        print(f"复制文件 '{filename}' 到目标目录。")

print("复制完成。")

# 第三段代码 - 检测交界点
import os
import torch
import numpy as np
import cv2
import pandas as pd
from PIL import Image

# 加载yoloV5模型
model = torch.hub.load('/home/lincha/tools/yolov5-master/yolov5-master', 'custom', path='/home/lincha/tools/yolov5-master/yolov5-master/runs/train/exp9/weights/best.pt', source='local', device='0')

# 目标目录
image_directory = '/home/lincha/tem5/adni/adni1/png_yes'

# 输出CSV文件路径
output_csv = 'output_boundary_coordinates.csv'

# 新目录用于保存rect_img的png图片
output_image_directory = '/home/lincha/tem5/adni/adni1/rect_images'
os.makedirs(output_image_directory, exist_ok=True)

# 用于存储输出结果
output_data = []

# 遍历目录中的所有图片
for filename in os.listdir(image_directory):
    if filename.endswith(".png"):
        img_path = os.path.join(image_directory, filename)
        img = cv2.imread(img_path)
        results = model(img_path)
        pred = results.xyxy[0]
        cls_0_data = [None] * 6
        cls_1_data = [None] * 6
        for row in pred:
            xmin, ymin, xmax, ymax, conf, cls = row
            if cls == 0:
                xmin = round(xmin.item())
                ymin = round(ymin.item())
                xmax = round(xmax.item())
                ymax = round(ymax.item())
                conf = float(conf.item())
                width = xmax - xmin
                height = ymax - ymin
                rect_img = img[ymin:ymax, xmin:xmax]
                rect_image_filename = f'{filename}_class_0.png'
                rect_image_path = os.path.join(output_image_directory, rect_image_filename)
                cv2.imwrite(rect_image_path, rect_img)
                lower_green = np.array([0, 130, 0], dtype=np.uint8)
                upper_green = np.array([80, 255, 80], dtype=np.uint8)
                lower_blue = np.array([140,70,0], dtype=np.uint8)
                upper_blue = np.array([220,200,60], dtype=np.uint8)
                green_mask = cv2.inRange(rect_img, lower_green, upper_green)
                blue_mask = cv2.inRange(rect_img, lower_blue, upper_blue)
                blue_coords = np.argwhere(blue_mask > 0)
                green_coords = np.argwhere(green_mask > 0)
                if green_coords.size > 0 and blue_coords.size > 0:
                    green_max_x = np.max(green_coords[:, 1])
                    blue_min_x = np.min(blue_coords[:, 1])
                    boundary_x = (green_max_x + blue_min_x) // 2
                    boundary_x += xmin
                    cls_0_data = [xmin, ymin, xmax, ymax, green_max_x, blue_min_x]
            elif cls == 1:
                xmin = round(xmin.item())
                ymin = round(ymin.item())
                xmax = round(xmax.item())
                ymax = round(ymax.item())
                conf = float(conf.item())
                width = xmax - xmin
                height = ymax - ymin
                rect_img = img[ymin:ymax, xmin:xmax]
                rect_image_filename = f'{filename}_class_1.png'
                rect_image_path = os.path.join(output_image_directory, rect_image_filename)
                cv2.imwrite(rect_image_path, rect_img)
                lower_blue = np.array([140,70,0], dtype=np.uint8)
                upper_blue = np.array([220,200,60], dtype=np.uint8)
                lower_green = np.array([0, 130, 0], dtype=np.uint8)
                upper_green = np.array([80, 255, 80], dtype=np.uint8)
                blue_mask = cv2.inRange(rect_img, lower_blue, upper_blue)
                green_mask = cv2.inRange(rect_img, lower_green, upper_green)
                green_coords = np.argwhere(green_mask > 0)
                blue_coords = np.argwhere(blue_mask > 0)
                if green_coords.size > 0 and blue_coords.size > 0:
                    blue_max_x = np.max(blue_coords[:, 1])
                    green_min_x = np.min(green_coords[:, 1])
                    boundary_x = (blue_max_x + green_min_x) // 2
                    boundary_x += xmin
                    cls_1_data = [xmin, ymin, xmax, ymax, blue_max_x, green_min_x]
        output_data.append([filename] + cls_0_data + cls_1_data)

# 创建DataFrame并保存为CSV文件
columns = ['filename', 'xmin_0', 'ymin_0', 'xmax_0', 'ymax_0', 'green_max_0', 'blue_min_0',
           'xmin_1', 'ymin_1', 'xmax_1', 'ymax_1', 'blue_max_1', 'green_min_1']

output_df = pd.DataFrame(output_data, columns=columns)
output_df.fillna(0, inplace=True)
output_df.to_csv(output_csv, index=False)

print("处理完成！结果已保存到", output_csv)

