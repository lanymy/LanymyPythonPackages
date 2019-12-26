"""

时间: 2016年01月13日

作者: 

文件: PathFunctions.py

描述: 路径相关辅助方法

其它:

"""
import os


def initFolderFullPath(folderFullPath):
    """
    目录路径初始化
    :param folderFullPath: 目录全路径
    :return:
    """
    if (not os.path.exists(folderFullPath)):
        os.makedirs(folderFullPath);
        pass;
    pass;


def getFileName(filePath,ifHaveExtensions = True):
    """
    :param filePath: 文件路径
    :param ifHaveExtensions: 返回的文件名是否包含后缀名 默认 True 包含
    :return:
    """

    resultFileName = None;

    if(ifHaveExtensions):
        resultFileName = os.path.basename(filePath);
        pass;
    else:
        resultFileName = os.path.split(os.path.splitext(filePath)[0])[1];
        pass;

    return resultFileName;

    pass;



if(__name__ == "__main__"):
    filename=r'E:\ebook\python\docs-pdf-2.7\c-api.pdf';
    filename = getFileName(filename,True);
    filename = getFileName(filename,False);
    pass;