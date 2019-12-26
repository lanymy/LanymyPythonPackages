"""

时间: 2016年01月18日

作者: 

文件: FtpClass.py

描述: FTP操作类

其它:

"""

from ftplib import FTP;
import os, sys, string, datetime, time;
import socket;
from LanymyPythonPackages import EnumFunctions;


# class __FtpServerType(Enum):
#     FileZilla = 0;
#     Red = 1;
#     Blue = 2;
#     # @classmethod
#     # def getEnum(cls,enumItemName):
#     #
#     #     enumItem = cls.FileZilla;
#     #     if(enumItemName == cls.FileZilla._name_):
#     #         pass;
#     #     pass;
#     pass;
#
#
# class __FtpServerFileInfoModel(object):
#     """
#     ftp服务器文件信息实体类
#     """
#
#     def __init__(self, ):
#         pass;
#
#     pass;


class FtpServerType(EnumFunctions.EnumAutoNumber):
    """
    FTP服务器类型枚举值
    """
    UnKnow = ();
    FileZilla = ();
    Microsoft = ();
    pass;


class FtpDirInfo(object):
    """
    ftp服务器目录内文件 文件夹信息
    """

    def __init__(self):
        self.DirPath = None;
        self.Files = [];
        self.Dirs = [];
        pass;

    pass;


class FtpClass(object):
    """
    FTP操作类
    """

    def __init__(self, hostAddress, ftpUserName, ftpPassword, ftpPort=21, ftpEncoding="UTF-8", ftpTimeout=300,
                 remoteDir="./"):
        """
        :param hostAddress: FTP服务器地址
        :param ftpUserName: 用户名
        :param ftpPassword: 密码
        :param ftpPort:端口
        :param ftpEncoding:ftp编码 默认utf-8
        :param ftpTimeout:FTP超时时间
        :param remoteDir:FTP服务器目录
        :return:
        """

        self.HostAddress = hostAddress;
        self.UserName = ftpUserName;
        self.Password = ftpPassword;
        self.RemoteDir = remoteDir;
        self.FtpEncoding = ftpEncoding;
        self.Port = ftpPort;
        self.Ftp = FTP();
        self.FtpTimeout = ftpTimeout;
        # self.FileList = [];
        self.BufferSize = 1024;
        self.FtpServerType = FtpServerType.UnKnow;
        pass;

    def __del__(self):
        if (self.Ftp):
            self.Ftp.close();
            pass;
        pass;

    def __enter__(self):
        return self;
        pass;

    def __exit__(self, exc_type, exc_val, exc_tb):
        # if (self.Ftp):
        #     self.Ftp.close();
        #     pass;
        self.__del__();
        pass;

    def __checkFtpServerType(self):
        """
        :return: 提取 ftp 服务器 版本类别
        """

        ftpWelcomeInfo = self.Ftp.getwelcome().lower();

        if (FtpServerType.FileZilla.name.lower() in ftpWelcomeInfo):
            self.FtpServerType = FtpServerType.FileZilla;
            pass;
        elif (FtpServerType.Microsoft.name.lower() in ftpWelcomeInfo):
            self.FtpEncoding = "GBK"
            self.FtpServerType = FtpServerType.Microsoft;
            pass


        pass;

    def login(self):
        ftp = self.Ftp;

        try:
            socket.setdefaulttimeout(self.FtpTimeout);
            ftp.set_pasv(True);
            # ftp.set_pasv(False);
            ftp.connect(self.HostAddress, self.Port);
            ftp.login(self.UserName, self.Password);
            pass;
        except Exception as e:
            raise Exception("连接 或 登陆 失败!");
            pass;

        try:
            # ftp.encoding = "UTF-8";
            # ftp.encoding = "ASCII";
            # ftp.encoding = "gb2312";
            # ftp.encoding = self.FtpEncoding;
            self.__checkFtpServerType();
            ftp.encoding = self.FtpEncoding;

            ftp.cwd(self.RemoteDir);
            # ftp.sendcmd("PASV");
            # ftp.sendcmd("OPTS UTF8 ON");
            pass;
        except(Exception):
            raise Exception("FTP服务器目录 {0} 切换失败".format(self.RemoteDir));
            pass;

        pass;

    def ifIsSameSize(self, localFile, remoteFile):
        """
        :param localFile: 本地文件全路径
        :param remoteFile: FTP服务器文件全路径
        :return: 比对两个文件 大小是否一致
        """
        try:
            remoteFileSize = self.Ftp.size(remoteFile)
        except:
            remoteFileSize = -1
        try:
            localFileSize = os.path.getsize(localFile)
        except:
            localFileSize = -1

        return remoteFileSize == localFileSize;

        pass;

    def downloadFile(self, localFile, remoteFile):
        """
        :param localFile: 本地保存文件全路径
        :param remoteFile: ftp服务器文件路径
        # :param preFix: 下载的ftp 文件 添加前缀标识  默认 None 则不加前缀标识  如 ftpPreFix.ftpfile.zip  ftpPreFix 就是添加的前缀
        :return:
        """
        if (self.ifIsSameSize(localFile, remoteFile)):
            # debug_print(u'%s 文件大小相同，无需下载' %localfile)
            return;
            pass;

        # return
        with open(localFile, 'wb') as fileHandler:
            self.Ftp.retrbinary("RETR {0}".format(remoteFile), fileHandler.write, self.BufferSize);
            # self.Ftp.retrbinary("RETR {0}".format(remoteFile), fileHandler.write);
            pass;

        pass;

    def downloadFiles(self, localDir='./', remoteDir='./'):
        """
        :param localDir: 保存ftp下载文件根目录
        :param remoteDir: ftp服务器 文件 目录
        # :param preFix: 下载的ftp 文件 添加前缀标识  默认 None 则不加前缀标识  如 ftpPreFix.ftpfile.zip  ftpPreFix 就是添加的前缀
        :return:
        """

        ftpDirInfo = self.getFtpDirInfo(remoteDir);

        # try:
        #     self.Ftp.cwd(remoteDir);
        #     pass;
        # except:
        #     raise Exception("目录{0}不存在，继续...".format(remoteDir));
        #     pass;

        if not os.path.isdir(localDir):
            os.makedirs(localDir);
            pass;

        # remoteNames = [];
        # self.Ftp.dir(remoteNames);
        # remoteNames = self.FileList;
        # # 0 = {str} '-rw-r--r-- 1 ftp ftp           1146 Jan 19 15:01 Config.ini'
        # # 1 = {str} 'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir1'
        # # 2 = {str} 'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir2'
        # # 3 = {str} '-rw-r--r-- 1 ftp ftp              0 Dec 31 10:10 新建文本文档 - 副本1.txt'
        # aaaa = self.Ftp.nlst();

        # for item in remoteNames:
        #
        #     fileType, fileName = self.__matchFtpFile(item);
        #
        #     local = os.path.join(localDir, fileName);
        #
        #     if fileType == 'd':
        #         self.downloadFiles(local, fileName);
        #         pass;
        #     elif fileType == '-':
        #         self.downloadFile(local, fileName);
        #         pass;
        #
        #     pass;

        for file in ftpDirInfo.Files:
            local = os.path.join(localDir, file);
            self.downloadFile(local, file);
            pass;

        for dir in ftpDirInfo.Dirs:
            local = os.path.join(localDir, dir);
            self.downloadFiles(local, dir);
            pass;

        self.Ftp.cwd('..');

        pass;

    def __matchFtpFile(self, ftpFileInfo):
        fileType = None;
        fileName = None;
        if (self.FtpServerType == FtpServerType.FileZilla):
            # FileZilla ftp server
            # remoteNames = self.FileList;
            # # 0 = {str} '-rw-r--r-- 1 ftp ftp           1146 Jan 19 15:01 Config.ini'
            # # 1 = {str} 'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir1'
            # # 2 = {str} 'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir2'
            # # 3 = {str} '-rw-r--r-- 1 ftp ftp              0 Dec 31 10:10 新建文本文档 - 副本1.txt'

            fileType = ftpFileInfo[0];
            fileName = ftpFileInfo.split(":", 1)[1][2:].strip();
            pass;
        elif (self.FtpServerType == FtpServerType.Microsoft):
            # Microsoft ftp server
            # 0 = {str} '01-19-16  01:13PM              1605144 20160118.zip'
            # 1 = {str} '01-20-16  08:00AM               502842 20160119.zip'
            # 2 = {str} '01-21-16  08:00AM               478305 20160120.zip'
            # 3 = {str} '01-22-16  08:00AM               548988 20160121.zip'
            # 4 = {str} '01-23-16  08:00AM               464388 20160122.zip'
            # 5 = {str} '01-23-16  08:00AM               464388 20160124.zip'
            # 6 = {str} '01-25-16  04:29PM       <DIR>          dirtest'
            fileInfoList = ftpFileInfo.split(":", 1)[1][4:].strip().split(" ", 1);
            fileType = fileInfoList[0];
            fileName = fileInfoList[1].strip();
            fileType = "d" if ("dir" in fileType.lower()) else "-";

            pass;

        return fileType, fileName;
        pass;

    def uploadFile(self, localFile, remoteDir, remoteFile):
        if not os.path.isfile(localFile):
            return;
            pass;

        if self.ifIsSameSize(localFile, remoteFile):
            return;
            pass;

        with open(localFile, 'rb')  as file_handler:
            self.Ftp.storbinary("STOR {0}".format(remoteFile), file_handler, self.BufferSize);
            pass;

        pass;

    def uploadFiles(self, localDir='./', remoteDir='./'):
        if not os.path.isdir(localDir):
            return;
            pass;
        localNames = os.listdir(localDir);
        self.initRemoteDir(remoteDir);
        self.Ftp.cwd(remoteDir);
        for item in localNames:
            src = os.path.join(localDir, item)
            if os.path.isdir(src):
                self.initRemoteDir(item);
                self.uploadFiles(src, item)
            else:
                self.uploadFile(src, remoteDir, item);
        self.Ftp.cwd('..')
        pass;

    def initRemoteDir(self, remoteDir):
        try:
            self.Ftp.mkd(remoteDir);
            pass;
        except:
            pass;
        pass;

    def getFtpDirInfo(self, remoteDir='./'):

        try:
            self.Ftp.cwd(remoteDir);
            pass;
        except:
            raise Exception("目录{0}不存在".format(remoteDir));
            pass;
        ftpDirInfo = FtpDirInfo();
        ftpDirInfo.DirPath = remoteDir;
        remoteNames = [];
        self.Ftp.dir(remoteNames.append);

        # FileZilla ftp server
        # remoteNames = self.FileList;
        # # 0 = {str} '-rw-r--r-- 1 ftp ftp           1146 Jan 19 15:01 Config.ini'
        # # 1 = {str} 'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir1'
        # # 2 = {str} 'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir2'
        # # 3 = {str} '-rw-r--r-- 1 ftp ftp              0 Dec 31 10:10 新建文本文档 - 副本1.txt'
        # aaaa = self.Ftp.nlst();

        # Microsoft ftp server
        # 0 = {str} '01-19-16  01:13PM              1605144 20160118.zip'
        # 1 = {str} '01-20-16  08:00AM               502842 20160119.zip'
        # 2 = {str} '01-21-16  08:00AM               478305 20160120.zip'
        # 3 = {str} '01-22-16  08:00AM               548988 20160121.zip'
        # 4 = {str} '01-23-16  08:00AM               464388 20160122.zip'
        # 5 = {str} '01-23-16  08:00AM               464388 20160124.zip'
        # 6 = {str} '01-25-16  04:29PM       <DIR>          dirtest'

        for item in remoteNames:

            fileType, fileName = self.__matchFtpFile(item);

            if fileType == 'd':
                ftpDirInfo.Dirs.append(fileName);
                pass;
            elif fileType == '-':
                ftpDirInfo.Files.append(fileName);
                pass;

            pass;

        return ftpDirInfo;

        pass;

    pass;


if __name__ == '__main__':
    # from LanymyPythonPackages import EnumFunctions;
    #
    # enumTemp = __FtpServerType.Red;
    #
    # stra = "123";
    #
    # a1 = type(stra);
    #
    # a1 = type(__FtpServerType);
    #
    # aaaaa = dir(__FtpServerType);
    #
    # aaaaa1= __FtpServerType._member_names_;
    # a2 = EnumFunctions.getEnumByKey(__FtpServerType,"Red1");
    # a3 = EnumFunctions.getEnumByValue(__FtpServerType,2);
    # print(enumTemp.name)
    # print(enumTemp.value)
    # print(__FtpServerType(0));
    # aaaa = __FtpServerType.__contains__(__FtpServerType.Red);
    #
    # # bbb = __FtpServerType.__getattr__("Red1");
    # # ccc = __FtpServerType.__dir__();
    # # print(__FtpServerType("Red"))
    #
    #
    #
    # # 0 = {str} '-rw-r--r-- 1 ftp ftp           1146 Jan 19 15:01 Config.ini'
    # # 1 = {str} 'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir1'
    # # 2 = {str} 'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir2'
    # # 3 = {str} '-rw-r--r-- 1 ftp ftp              0 Dec 31 10:10 新建文本文档 - 副本1.txt'
    #
    # ftpNameList = ['-rw-r--r-- 1 ftp ftp           1146 Jan 19 15:01 Config.ini',
    #                'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir1',
    #                'drwxr-xr-x 1 ftp ftp              0 Jan 19 16:43 dir2',
    #                '-rw-r--r-- 1 ftp ftp              0 Dec 31 10:10 新建文本文档 - 副本1.txt',
    #                ];

    # 0 = {str} 'drwxr-xr-x    2 0        0            4096 Aug 18 10:52 backup'
    # 1 = {str} 'drwxr-xr-x    2 0        0            4096 Jan 20 03:40 ftplogs'
    # 2 = {str} 'drwxr-xr-x    7 641      100          4096 Jan 07 18:13 htdocs'
    # 3 = {str} 'drwxr-xr-x    2 641      100          4096 Dec 30 15:04 myfolder'
    # 4 = {str} 'drwxr-xr-x    2 0        0            4096 Jan 20 02:02 wwwlogs'
    # 5 = {str} '-r-xr--r--    1 0        0             606 Feb 03  2015 ÇëÏÈ¶ÁÎÒ.txt'

    # timenow  = time.localtime()
    # datenow  = time.strftime('%Y-%m-%d', timenow)
    # 配置如下变量
    # todo 提交的时候去掉帐号信息
    hostAddr = ''  # ftp地址
    userName = ''  # 用户名
    password = ''  # 密码
    port = 21  # 端口号
    rootdirRemote = '/deals/dirtest/20160125/'  # 远程目录

    # hostAddr = ''  # ftp地址
    # userName = ''  # 用户名
    # password = ''  # 密码
    # port =   # 端口号
    # rootdirRemote = './'  # 远程目录

    rootdirLocal = r''  # 本地目录

    with FtpClass(hostAddr, userName, password, port,"GBK") as ftp:
        ftp.login();
        ftpDirInfo = ftp.getFtpDirInfo(rootdirRemote);

        pass;

    # f = FtpClass(hostAddr, userName, password, port);
    # f.login()
    # localTemp = os.path.join(rootdirLocal, "Config.ini");
    # # f.downloadFile(localTemp,"./Config.ini");
    # f.downloadFiles(rootdirLocal, rootdirRemote)
    #
    # # f.uploadFile(localTemp,"./Config.ini");
    # # f.uploadFiles(rootdirLocal,"./testDir");
    #
    # #
    # # timenow  = time.localtime()
    # # datenow  = time.strftime('%Y-%m-%d', timenow)
    # # logstr = u"%s 成功执行了备份\n" %datenow
    # # debug_print(logstr)
    pass;
