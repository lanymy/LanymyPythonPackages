"""

时间: 2016年01月11日

作者: 

文件: ZipFunctions.py

描述: 压缩包相关操作

其它:

"""

import os
import zipfile
import fnmatch;
from LanymyPythonPackages import PathFunctions;


def zipDir(sourceDirFullPath, zipFileFullPath, ifAppend=False, fileNames=None, preFix=None):
    """
    :param sourceDirFullPath: 要压缩的跟目录全路径
    :param zipFileFullPath: 压缩到目标 全路径
    :param ifAppend: 压缩行为 True 向压缩包追加文件 False 覆盖模式重新创建压缩包
    :param fileNames:要压缩的文件组 支持通配符  默认值 * 所有文件
    :param preFix: 压缩包里每个文件的前缀 默认为空 则 不加前缀处理
    :return:
    """

    defaultFileNames = ["*"];

    if (not fileNames or "*" in fileNames):
        fileNames = defaultFileNames;
        pass;

    fileList = []

    if not os.path.exists(sourceDirFullPath):
        raise IOError("要压缩的源路径 {0}  不存在!".format(sourceDirFullPath));
        pass;

    # 数据有效性效验匹配

    if os.path.isdir(zipFileFullPath):
        tmpBaseName = os.path.basename(sourceDirFullPath);
        zipFileFullPath = os.path.normpath(os.path.join(zipFileFullPath, tmpBaseName + ".zip"));
        pass;

    zipFileDirFullPath = os.path.split(zipFileFullPath)[0];
    if (not os.path.exists(zipFileDirFullPath)):
        os.makedirs(zipFileDirFullPath);
        pass;

    if os.path.isfile(sourceDirFullPath):
        # fileList.append(os.path.join(os.path.dirname(sourceDirFullPath),"{0}.{1}".format(preFix,os.path.basename(sourceDirFullPath))) if preFix else sourceDirFullPath);
        fileList.append(sourceDirFullPath);
        sourceDirFullPath = os.path.dirname(sourceDirFullPath);
        pass;
    else:
        for root, dirList, files in os.walk(sourceDirFullPath):
            for item in fileNames:
                matchFileNames = fnmatch.filter(files, item);
                for fileName in matchFileNames:
                    # fileList.append(os.path.join(root, ("{0}.{1}".format(preFix,fileName) if preFix else fileName)));
                    fileList.append(os.path.join(root, fileName));
                    pass;
                pass;
            pass;

    with zipfile.ZipFile(zipFileFullPath, "a" if ifAppend else "w") as destZip:
        for eachFile in fileList:
            destFile = eachFile[len(sourceDirFullPath):];
            if (preFix):
                destFile = os.path.join(os.path.dirname(destFile),"{0}.{1}".format(preFix,os.path.basename(destFile)));
                pass;
            destZip.write(eachFile, destFile);
        pass;

    pass;


if __name__ == '__main__':
    sourcePath = r"";
    targetPath = r"";

    zipDir(sourcePath, targetPath);

    pass;
