"""

时间: 2016年01月05日

作者: 

文件: FileFunctions.py

描述: 

其它:

"""


import os;
import shutil;



# class FileFunctions(object):
#     """文件操作辅助类"""



def copyDir(sourceDir, targetDir):
    """目录拷贝
    :param sourceDir: 源目录路径
    :param targetDir: 复制目标目录路径
    """
    for dirPath, dirNames, fileNames in os.walk(sourceDir):

        # 创建目录
        for dirName in dirNames:
            theTargetDirPath = os.path.join(dirPath, dirName).replace(sourceDir, targetDir);
            # print(theTargetDirPath);
            if (not os.path.exists(theTargetDirPath)):
                os.makedirs(theTargetDirPath);

        # 复制文件
        for fileName in fileNames:
            sourceFileFullPath = os.path.join(dirPath, fileName);
            targetFileFullPath = sourceFileFullPath.replace(sourceDir, targetDir)
            try:
                # if (os.path.splitext(theFile)[1] == ".txt"):
                #     print('Fount rpm package: ' + theFile);
                copyFile(sourceFileFullPath, targetFileFullPath);
            except IOError as err:
                print(err);

def copyFile(sourceFileFullPath,targetFileFullPath):
    """文件拷贝
    :param sourceFileFullPath:源文件全路径
    :param targetFileFullPath:要拷贝到的 目标文件全路径
    """
    if(os.path.isfile(sourceFileFullPath)):
        shutil.copy(sourceFileFullPath, targetFileFullPath);



if (__name__ == '__main__'):
    sourcePath = r"";
    targetPath = r"";
    copyDir(sourcePath, targetPath);
