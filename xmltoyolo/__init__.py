from xml.dom import minidom
import os, glob
from tqdm import tqdm


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

classes = {}

def read_class(class_file):
    try:
        with open(class_file, 'r') as f:
            for line in f:
                line = line.strip()
                classes[line] = len(classes)
    except:
        print (f"{bcolors.FAIL}Error: Class File Path is not valid. Cannot open file.{bcolors.ENDC}")
        return True

def convert_coordinates(size, box):
    dw = 1.0/size[0]
    dh = 1.0/size[1]
    x = (box[0]+box[1])/2.0
    y = (box[2]+box[3])/2.0
    w = box[1]-box[0]
    h = box[3]-box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)


def convert_xml2yolo(class_path = '.', annotation_path = '.', output_path = '.'):
    if read_class(class_path): return
    if not os.path.exists(output_path): 
        os.makedirs(output_path)
        print("Created output directory: ", output_path)
    if not os.path.exists(annotation_path): 
        print(f"{bcolors.FAIL}Error: Annotation Path is not valid.{bcolors.ENDC}")
        return
    
    try:
        for fname in tqdm(glob.glob(os.path.join(annotation_path, "*.xml"))):
            xmldoc = minidom.parse(fname)
            fname_out = os.path.join(output_path, os.path.basename(fname)[:-4]+'.txt')
            with open(fname_out, "w") as f:
                itemlist = xmldoc.getElementsByTagName('object')
                size = xmldoc.getElementsByTagName('size')[0]
                width = int((size.getElementsByTagName('width')[0]).firstChild.data)
                height = int((size.getElementsByTagName('height')[0]).firstChild.data)
                for item in itemlist:
                    # get class label
                    classid =  (item.getElementsByTagName('name')[0]).firstChild.data
                    if classid in classes:
                        label_str = str(classes[classid])
                    else:
                        label_str = "-1"
                        print ("warning: label '%s' not in look-up table" % classid)

                    # get bbox coordinates
                    xmin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmin')[0]).firstChild.data
                    ymin = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymin')[0]).firstChild.data
                    xmax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('xmax')[0]).firstChild.data
                    ymax = ((item.getElementsByTagName('bndbox')[0]).getElementsByTagName('ymax')[0]).firstChild.data
                    b = (float(xmin), float(xmax), float(ymin), float(ymax))
                    bb = convert_coordinates((width,height), b)
                    f.write(label_str + " " + " ".join([("%.6f" % a) for a in bb]) + '\n')
    except Exception as e:
        print (f"{bcolors.FAIL}Error: {e}{bcolors.ENDC}")
        return True
