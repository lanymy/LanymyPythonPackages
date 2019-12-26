"""

时间: 2016年01月20日

作者: 

文件: EmailFunctions.py

描述: 邮件操作类

其它:

"""

import imaplib;
import email;
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
import re
import time
# from hashlib import md5;
from LanymyPythonPackages import EnumFunctions;
from LanymyPythonPackages import CustomDecorators;
from LanymyPythonPackages import PathFunctions;
import datetime;


class MailFlagEnum(EnumFunctions.EnumAutoNumber):
    """
    邮件标记枚举值
    """
    All = ();
    Unseen = ();
    Seen = ();
    Recent = ();
    Answered = ();
    Flagged = ();
    pass;


class MailFolder(object):
    """
    邮箱文件夹信息实体类
    """

    # flags, delimiter, folder_name
    def __init__(self, flags=None, delimiter=None, folderName=None):
        """
        :param flags: 标记
        :param delimiter: 分隔符
        :param folderName: 文件夹名称
        :return:
        """

        self.Flags = flags;
        self.Delimiter = delimiter;
        self.FolderName = folderName;

        pass;

    pass;


class MailDigest(object):
    """
    邮件摘要信息实体类
    """

    @CustomDecorators.accepts(object, object, str, str, str, datetime.date, email.message.Message)
    def __init__(self, mailID=None, mailFrom=None, mailTo=None, mailSubject=None, mailDate=None, mailMessage=None):
        """
        :param mailID: 邮件ID标识
        :param mailFrom: 发件方
        :param mailTo: 收件方
        :param mailSubject: 标题
        :param mailDate: 日期
        :return:
        """
        self.MailID = mailID;
        self.MailFrom = mailFrom;
        self.MailTo = mailTo;
        self.MailSubject = mailSubject;
        self.MailDate = mailDate;
        self.MailMessage = mailMessage;
        pass;

    pass;


class ImapClass(object):
    """
    接收邮件操作类
    """

    # 不用ssl连接默认端口号
    __UN_SSL_DEFAULT_PORT = 143;
    # 使用ssl连接默认端口号
    __SSL_DEFAULT_PORT = 993;
    # 邮箱文件夹信息解析正则表达式
    __LIST_PATTERN = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)');
    # 保存邮件附件文件名格式化字符串
    __MAIL_ATTACH_FILE_NAME_FORMAT = "mail[{0}].attach.{1}";
    # 保存邮件内容文件名格式化字符串
    __MAIL_CONTENT_FILE_NAME_FORMAT = "mail[{0}].content{1}";

    def __init__(self, host, userName, password, ifUseSSL=True, port=None):
        # try:
        #
        #     # print("[+] Connect to {0}:{1} successfully".format(host, port))
        #     pass;
        # except Exception as e:
        #     exit_script("Connect to {0}:{1} failed".format(host, port), e);
        #     pass;

        if (not port):
            port = ImapClass.__SSL_DEFAULT_PORT if ifUseSSL else ImapClass.__UN_SSL_DEFAULT_PORT;
            pass;

        imapClient = imaplib.IMAP4_SSL(host, port) if ifUseSSL else imaplib.IMAP4(host, port);
        imapClient.login(userName, password);

        self.ImapClient = imapClient;
        self.UserName = userName;

        pass;

    def __del__(self):
        if (self.ImapClient):
            self.ImapClient.close();
            self.ImapClient.logout();
            pass;
        pass;

    def __enter__(self):
        return self;
        pass;

    # __exit__ 在 __del__ 之前执行
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__();
        pass;

    def getMailFolders(self):
        """
        :return: 获取邮箱 文件夹 集合
        """

        foldersList = [];

        type_, folders = self.ImapClient.list();

        for folder in folders:
            try:
                flags, delimiter, folderName = ImapClass.__LIST_PATTERN.match(folder.decode()).groups();
                folderName = folderName.strip('"');
                print("[*] Handling folder: {0}".format(folderName));
                foldersList.append(MailFolder(flags, delimiter, folderName));
                pass;
            except Exception as e:
                print("[-] Parse folder {0} failed: {1}".format(folder, e));
                continue;
                pass;

        return foldersList;
        pass;

    @CustomDecorators.accepts(object, MailFlagEnum, int)
    def getMailDigestList(self, mailFlagEnum=MailFlagEnum.All, newMailTopNum=10):
        """
        目前只能操作收件箱里的邮件信息 传入 初始化 其它邮件文件夹信息  原生api 操作报错
        :param mailFlagEnum: 邮件过滤标记 默认 All 全部邮件
        :param newMailTopNum: 提取最新邮件的多少封 进行处理
        :return: 返回收件箱符合邮件标记的 所有 邮件摘要信息 From  To  SendDate 等
        """

        imapClient = self.ImapClient;

        imapClient.select("INBOX");
        type_, data = imapClient.search(None, mailFlagEnum.name);
        mailIDList = data[0].split();

        if (len(mailIDList) > newMailTopNum):
            mailIDList.reverse();
            mailIDList = mailIDList[:newMailTopNum];
            pass;

        mailDigestList = [];

        for mailID in mailIDList:
            type_, data = imapClient.fetch(mailID, "(RFC822)");
            msg = email.message_from_bytes(data[0][1]);
            strFrom = None;
            strTo = None;
            strSubject = None;
            strDate = None;

            # 解析from
            fromList = msg["From"].split(' ');
            if (len(fromList) == 2):  # 有别名
                fromName = email.header.decode_header((fromList[0]).strip('\"'));
                strFrom = self.__mailStringDecode(fromName[0][0], fromName[0][1]) + fromList[1];
                pass;
            else:
                strFrom = msg["From"];
                pass;

            strTo = msg["To"];
            # 获取Date
            strDate = msg["Date"];

            # 获取Subject
            subject = email.header.decode_header(msg["Subject"]);
            strSubject = self.__mailStringDecode(subject[0][0], subject[0][1]);

            mailDigestList.append(
                    MailDigest(mailID, strFrom, strTo, strSubject, self.mailDateToDate(strDate).date(), msg));

            pass;  # end for mailID in mailIDList

        return mailDigestList;

        pass;  # end getMailDigestList

    @CustomDecorators.accepts(object, str, MailFlagEnum, bool, str, str, datetime.date, datetime.date)
    def downLoadMail(self, saveMailDirFullPath, mailFlagEnum=MailFlagEnum.All, ifMarkMailFlagSeen=False,
                     fromKeyWord=None, toKeyWord=None, subjectKeyWord=None, startDate=None,
                     endDate=None):
        """
        目前只能操作收件箱里的邮件信息 传入 初始化 其它邮件文件夹信息  原生api 操作报错
        :param saveMailDirFullPath: 保存邮件文件夹全路径
        :param mailFlagEnum:要操作邮件的标记 如:未读邮件
        :param ifMarkMailFlagSeen:是否标记下载完成的邮件为已读
        :param fromKeyWord:from 搜索关键字 多个 用 ',' 分割
        :param toKeyWord:to 搜索关键字 多个 用 ',' 分割
        :param subjectKeyWord:搜索邮件的 起始 日期
        :param startDate:搜索邮件的 起始 日期
        :param endDate:搜索邮件的 结束 日期
        :return:
        """
        # saveMailDirFullPath = os.path.join(saveMailDirFullPath, self.UserName);
        PathFunctions.initFolderFullPath(saveMailDirFullPath);

        strSplitChar = ",";

        fromKeyWords = [];
        toKeyWords = [];
        subjectKeyWords = [];

        if (fromKeyWord):
            fromKeyWords.extend(fromKeyWord.split(strSplitChar));
            pass;

        if (toKeyWord):
            toKeyWords.extend(toKeyWord.split(strSplitChar));
            pass;

        if (subjectKeyWord):
            subjectKeyWords.extend(subjectKeyWord.split(strSplitChar));
            pass;

        imapClient = self.ImapClient;

        imapClient.select("INBOX");
        type_, data = imapClient.search(None, mailFlagEnum.name);
        mailIDList = data[0].split();

        for mailID in mailIDList:
            type_, data = imapClient.fetch(mailID, "(RFC822)");
            msg = email.message_from_bytes(data[0][1]);
            strFrom = None;
            strTo = None;
            strSubject = None;
            strDate = None;

            # 解析from
            fromList = msg["From"].split(' ');
            if (len(fromList) == 2):  # 有别名
                fromName = email.header.decode_header((fromList[0]).strip('\"'));
                strFrom = self.__mailStringDecode(fromName[0][0], fromName[0][1]) + fromList[1];
                pass;
            else:
                strFrom = msg["From"];
                pass;

            strTo = msg["To"];

            # 获取Date
            strDate = msg["Date"];

            # 获取Subject
            subject = email.header.decode_header(msg["Subject"]);
            strSubject = self.__mailStringDecode(subject[0][0], subject[0][1]);

            mailDigest = MailDigest(mailID, strFrom, strTo, strSubject, self.mailDateToDate(strDate).date(), msg);
            if (self.checkMailDigest(mailDigest, fromKeyWords, toKeyWords, subjectKeyWords, startDate, endDate)):
                # 符合检索要求的邮件 下载
                self.downLoadMailByMailDigest(saveMailDirFullPath, mailDigest);
                if (ifMarkMailFlagSeen):
                    # 标记此邮件状态为已读
                    imapClient.store(mailID, '+FLAGS', '\\Seen');
                    pass;

                pass;  # end if

            pass;  # end for mailID in mailIDList

        pass;  # end downLoadMail

    @CustomDecorators.accepts(object, str, MailDigest, list)
    def downLoadMailByMailDigest(self, saveMailDirFullPath, mailDigest, mailContentKeyWordList=None):
        # Parse and save email content and attachments

        saveFileFullPath = "";

        for part in mailDigest.MailMessage.walk():
            if not part.is_multipart():

                contentType = part.get_content_type();
                fileName = part.get_filename();
                charset = part.get_content_charset();
                content = part.get_payload(decode=True);

                if fileName:  # Attachment
                    # Decode filename

                    fileNameDecode = email.header.decode_header(fileName);
                    fName = self.__mailStringDecode(fileNameDecode[0][0], fileNameDecode[0][1]);
                    saveFileFullPath = os.path.join(saveMailDirFullPath,
                                                    ImapClass.__MAIL_ATTACH_FILE_NAME_FORMAT.format(
                                                            mailDigest.MailID.decode(),
                                                            fName));
                else:  # Main content
                    suffix = ".unknown";
                    if contentType in ['text/plain']:
                        suffix = '.txt'
                    if contentType in ['text/html']:
                        suffix = '.htm'

                    # if (mailContentKeyWordList):
                    #     matchMailContent = False;
                    #     contentTemp = email.header.decode_header(content);
                    #     contentTemp = self.__mailStringDecode(contentTemp[0][0], contentTemp[0][1]);
                    #     contentTemp = contentTemp.lower();
                    #     for item in mailContentKeyWordList:
                    #         if (item.lower() in contentTemp):
                    #             matchMailContent = True;
                    #             break;
                    #             pass;
                    #         pass;
                    #
                    #     if (not matchMailContent):
                    #         return;
                    #         pass;
                    #
                    #     pass;

                    saveFileFullPath = os.path.join(saveMailDirFullPath,
                                                    ImapClass.__MAIL_CONTENT_FILE_NAME_FORMAT.format(
                                                            mailDigest.MailID.decode(), suffix));
                    pass;

                with open(saveFileFullPath, "wb") as f:
                    f.write(content);
                    pass;

                pass;  # end if
            pass;  # end for
        pass;  # end downLoadMailByMailDigest

    def __mailStringDecode(self, s, encoding):
        if encoding:
            # return unicode(s, encoding)
            return s.decode(encoding);
            pass;
        else:
            # return unicode(s)
            return s;
            pass;
        pass;  # end __mailStringDecode

    def mailDateToDate(self, strMailDate):
        """
        :return: 解析邮件的字符串格式日期 成 日期对象
        """
        # 'Wed, 23 Dec 2015 21:51:34 +0800 (CST)'

        strMailDate = " ".join(strMailDate.split()[0:5]);
        strDateFormate = "%a, %d %b %Y %H:%M:%S";

        return datetime.datetime.strptime(strMailDate, strDateFormate);

        pass;  # end mailDateToDate

    @CustomDecorators.accepts(object, MailDigest, list, list, list, datetime.date, datetime.date)
    @CustomDecorators.returns(bool)
    def checkMailDigest(self, mailDigest, fromKeyWords=None, toKeyWords=None, subjectKeyWords=None, startDate=None,
                        endDate=None):
        """
        根据条件 检查 此 邮件信息 是否 符合下载条件
        :return: 符合下载条件 True 否则 False
        """

        if (not mailDigest):
            return False;
            pass;

        if (fromKeyWords and len(fromKeyWords) > 0):
            result = False;
            for fromKeyWord in fromKeyWords:
                if (fromKeyWord in mailDigest.MailFrom):
                    result = True;
                    break;
                    pass;
                pass;
            if (not result):
                return False;
                pass;
            pass;

        if (toKeyWords and len(toKeyWords) > 0):
            result = False;
            for toKeyWord in toKeyWords:
                if (toKeyWord in mailDigest.MailTo):
                    result = True;
                    break;
                    pass;
                pass;
            if (not result):
                return False;
                pass;
            pass;

        if (subjectKeyWords and len(subjectKeyWords) > 0):
            result = False;
            for subjectKeyWord in subjectKeyWords:
                if (subjectKeyWord in mailDigest.MailSubject):
                    result = True;
                    break;
                    pass;
                pass;
            if (not result):
                return False;
                pass;
            pass;

        if (startDate and endDate and (
                        mailDigest.MailDate < startDate or mailDigest.MailDate > endDate)):  # 开始日期 结束日期 必须都有值
            return False;
            pass;

        return True;

        pass;  # end checkMailDigest

    pass;  # end ImapClass


# region 原生imap

#
# # Configuration
# # -------------
# #
# # Email address
# #
# #
# # MAILADDR = "username@163.com"
# #
# # # Email password
# # PASSWORD = "password"
# #
# # # Mail Server (pop/imap)
# # SERVER = "pop.163.com"
#
# # Transfer protocol (pop3/imap4)
# PROTOCOL = "imap4"
#
# # Use SSL? (True/False)
# USE_SSL = False
#
# # Main output direcotory
# OUTDIR = "result"
#
# # Static variable
# # ---------------
#
# # Default port of each protocol
# DEFAULT_PORT = {
#     "pop3": {False: 110, True: 995},
#     "imap4": {False: 143, True: 993},
# }
#
#
# # Function
# # --------
#
# def exit_script(reason, e=""):
#     """Print error reason and exit this script
#
#     :param reason: exit error reason
#     :param e: exception
#     """
#     # Print exit string
#     exit_str = "[-] {0}".format(reason)
#     if e:
#         exit_str += " ({0})".format(e)
#     print(exit_str)
#
#     # Remove result path
#     remove_dir(result_path)
#
#     # Exit script
#     print("[-] Fetch email failed!")
#     exit(-1)
#
#
# def parse_protocol(protocol):
#     """Parse transfer protocol
#
#     :param protocol: transfer protocol
#     :return: handled protocol
#     """
#     if protocol in ["pop", "pop3"]:
#         return "pop3"
#     elif protocol in ["imap", "imap4"]:
#         return "imap4"
#     else:
#         exit_script("Parse protocol failed: {0}".format(protocol))
#
#
# def parse_server(server, use_ssl, protocol):
#     """Change server to host and port. If no port specified, use default value
#
#     :param server: mail server (host, host:port)
#     :param use_ssl: True if use SSL else False
#     :param protocol: transfer protocol (pop3/imap4)
#     :return: host and port
#     """
#     if not server:
#         exit_script("No available server")
#
#     server_item = server.split(":")
#     server_item_len = len(server_item)
#
#     if server_item_len > 2:
#         exit_script("Too many colons in server: {0}".format(server))
#
#     try:
#         host = server_item[0]
#         port = DEFAULT_PORT[protocol][use_ssl] if server_item_len == 1 else int(server_item[1])
#     except BaseException as e:
#         exit_script("Parse server format failed: {0}".format(server), e)
#     return host, port
#
#
# def create_dir(result_path):
#     """Create output directory if not exist
#
#     :param result_path: main result path
#     """
#     try:
#         if not os.path.exists(result_path):
#             os.mkdir(result_path)
#             print("[*] Create directory {0} successfully".format(result_path))
#         else:
#             if os.path.isfile(result_path):
#                 exit_script("{0} is file".format(result_path))
#             else:
#                 print("[*] Directory {0} has already existed".format(result_path))
#     except BaseException as e:
#         exit_script("Create directory {0} failed".format(result_path), e)
#
#
# def remove_dir(result_path):
#     """Remove output directory if no file in this directory
#
#     :param result_path: main result path
#     """
#     try:
#         if os.path.isdir(result_path):
#             if len(os.listdir(result_path)) == 0:
#                 os.rmdir(result_path)
#                 print("[*] Remove directory {0} successfully".format(result_path))
#             else:
#                 print("[*] Directory {0} is not empty, no need remove".format(result_path))
#         else:
#             print("[*] No directory {0}".format(result_path))
#     except BaseException as e:
#         print("[-] Remove directory {0} failed: {1}".format(result_path, e))
#
#
# def imap4(host, port, usr, pwd, use_ssl):
#     """Imap4 handler
#
#     :param host: host
#     :param port: port
#     :param usr: username
#     :param pwd: password
#     :param use_ssl: True if use SSL else False
#     """
#     # Connect to mail server
#     try:
#         conn = imaplib.IMAP4_SSL(host, port) if use_ssl else imaplib.IMAP4(host, port)
#         conn.login(usr, pwd)
#         print("[+] Connect to {0}:{1} successfully".format(host, port))
#     except BaseException as e:
#         exit_script("Connect to {0}:{1} failed".format(host, port), e)
#
#     # Initial some variable
#     list_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
#     download_num = 0
#     download_hash = []
#
#     # Get all folders
#     try:
#         type_, folders = conn.list()
#     except BaseException as e:
#         exit_script("Get folder list failed", e)
#
#     for folder in folders:
#         # Parse folder info and get folder name
#         # folder=b'(\\HasNoChildren) "/" "Sent Messages"';
#         try:
#             flags, delimiter, folder_name = list_pattern.match(folder.decode()).groups()
#             folder_name = folder_name.strip('"')
#             print(
#                     "[*] Handling folder: {0}".format(folder_name))
#         except Exception as e:
#             print("[-] Parse folder {0} failed: {1}".format(folder, e))
#             continue
#
#         # Select and search folder
#         try:
#             # conn.select(folder_name, readonly=True)
#             conn.select(folder_name)
#
#             # type_, data = conn.search(None, "ALL")
#             type_, data = conn.search(None, "Unseen")
#
#             # data1 = data[0].split()[0]
#             # conn.store(data1, '+FLAGS', '\\Seen')
#
#             # type_, data = conn.search(None, 'From', '"邮箱地址"')
#             # type_, data = conn.search(None, '(OR (FROM "邮箱地址"))')
#             # type_, data = conn.search(None, '(OR (SUBJECT "邮箱地址"))')
#
#             # type_, data = conn.uid('search', None, '(OR (FROM "邮箱地址"))')
#
#
#             pass;
#         except BaseException as e:
#             print("[-] Search folder {0} failed: {1}".format(folder_name, e))
#             continue
#             pass;
#
#         # Get email number of this folder
#         try:
#             # msg_id_list = [int(i) for i in data[0].split()]
#             msg_id_list = data[0].split();
#             msg_num = len(msg_id_list)
#             print("[*] {0} emails found in {1} ({2})".format(msg_num, usr, folder_name))
#         except BaseException as e:
#             print("[-] Can't get email number of {0}: {1}".format(folder_name, e))
#             continue
#
#         # Get email content and attachments
#         for i in msg_id_list:
#             print("[*] Downloading email {0}/{1}".format(i, msg_num))
#
#             # Get email message
#             try:
#                 type_, data = conn.fetch(i, "(RFC822)");
#                 msg = email.message_from_bytes(data[0][1]);
#             except BaseException as e:
#                 print("[-] Retrieve email {0} failed: {1}".format(i, e))
#                 continue
#
#             ls = msg["From"].split(' ')
#             strfrom = ''
#             if (len(ls) == 2):
#                 fromname = email.header.decode_header((ls[0]).strip('\"'))
#                 strfrom = 'From : ' + my_unicode(fromname[0][0], fromname[0][1]) + ls[1]
#             else:
#                 strfrom = 'From : ' + msg["From"]
#             strdate = 'Date : ' + msg["Date"]
#             subject = email.header.decode_header(msg["Subject"])
#             sub = my_unicode(subject[0][0], subject[0][1])
#             strsub = 'Subject : ' + sub
#
#             # If message already exist, skip this message
#             try:
#                 msg_md5 = md5(data[0][1]).hexdigest()
#                 if msg_md5 in download_hash:
#                     print("[-] This email has been downloaded in other folder");
#                     continue
#                 else:
#                     download_hash.append(msg_md5)
#                     download_num += 1
#                 pass;
#             except BaseException as e:
#                 print("[-] Parse message md5 failed: {0}".format(e))
#                 continue
#
#             # Parse and save email content/attachments
#             try:
#                 parse_email(msg, download_num)
#             except BaseException as e:
#                 print("[-] Parse email {0} failed: {1}".format(i, e))
#
#     # Logout this account
#     conn.logout()
#
#
# # 字符编码转换方法
# def my_unicode(s, encoding):
#     if encoding:
#         # return unicode(s, encoding)
#         return s.decode(encoding);
#         pass;
#     else:
#         # return unicode(s)
#         return s;
#         pass;
#
#
# def parse_email(msg, i):
#     """Parse email message and save content & attachments to file
#
#     :param msg: mail message
#     :param i: ordinal number
#     """
#     global result_file
#
#     # Parse and save email content and attachments
#     for part in msg.walk():
#         if not part.is_multipart():
#             contenttype = part.get_content_type()
#             filename = part.get_filename()
#             # charset = part.get_charsets();
#             # if(len(charset)>0):
#             #     charset = charset[0];
#             #     pass;
#             # else:
#             #     charset = None;
#             #     pass;
#
#             charset = part.get_content_charset();
#
#             # charset = part.get_content_charset();
#
#             # content = part.get_payload(decode=True);
#
#             content = part.get_payload(decode=True)
#
#             if filename:  # Attachment
#                 # Decode filename
#
#                 filenameDecode = email.header.decode_header(filename)
#                 fname = my_unicode(filenameDecode[0][0], filenameDecode[0][1])
#
#                 # filename = dh[0][0]
#                 # fname = dh[0][0]
#                 # encodeStr = dh[0][1]
#                 # if encodeStr != None:
#                 #     if charset == None:
#                 #         fname = fname.decode(encodeStr, 'gbk')
#                 #     else:
#                 #         fname = fname.decode(encodeStr, charset)
#                 print('Attachment : ' + fname)
#                 result_file = os.path.join(result_path, "mail{0}_attach_{1}".format(i, fname))
#             else:  # Main content
#                 if contenttype in ['text/plain']:
#                     suffix = '.txt'
#                 if contenttype in ['text/html']:
#                     suffix = '.htm'
#                 # if charset == None:
#                 #     content = part.get_payload(decode=True)
#                 # else:
#                 #     content = part.get_payload(decode=True).decode(charset)
#                 # return  (mailContent, suffix)
#
#                 result_file = os.path.join(result_path, "mail{0}_text".format(i))
#                 pass;
#
#             try:
#                 with open(result_file, "wb") as f:
#                     f.write(content)
#             except BaseException as e:
#                 print("[-] Write file of email {0} failed: {1}".format(i, e))
#         pass;
#
#     pass;
#
#
# def get_charset(message, default="ascii"):
#     # Get the message charset
#     return message.get_charset();
#     return default;
#     pass;


# endregion


class SmtpClass(object):
    """
    发送邮件 操作类
    """

    def __init__(self, host, userName, password, port=25):
        """
        :param host: SMTP服务器
        :param userName: 用户名
        :param password: 密码
        :param port: 端口
        :return:
        """
        smtpClient = smtplib.SMTP();
        smtpClient.connect(host, port);
        smtpClient.login(userName, password);

        self.SmtpClient = smtpClient;
        self.UserName = userName;

        pass;

    def __del__(self):
        if (self.SmtpClient):
            self.SmtpClient.quit();
            pass;
        pass;

    def __enter__(self):
        return self;
        pass;

    # __exit__ 在 __del__ 之前执行
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__del__();
        pass;

    @CustomDecorators.accepts(object, list, str, str, str)
    def sendMail(self, sendTo, mailSubject, mailContent=None, mailEncoding="UTF-8"):
        """
        目前此API只支持 邮件正文 为 文本 text 形式
        如需要其它格式 再扩充
        :param sendTo: 发送给谁 list 列表 多发
        :param mailSubject: 标题
        :param mailContent: 邮件内容
        :param mailEncoding: 邮件编码格式
        :return:
        """

        msg = MIMEText(mailContent, 'plain', mailEncoding);
        msg['Subject'] = email.header.Header(mailSubject, mailEncoding);
        msg['From'] = self.UserName;
        msg['To'] = ";".join(sendTo);

        self.SmtpClient.sendmail(self.UserName, sendTo, msg.as_string());

        pass;

    pass;


if (__name__ == "__main__"):
    # todo 提交的时候去掉帐号信息
    imapServer = "imap.exmail.qq.com";
    imapUserame = "邮箱地址";
    imapPwd = "";

    smtpServer = "smtp.exmail.qq.com";
    smtpUserame = "邮箱地址";
    smtpPwd = "";

    # from imapclient import IMAPClient;
    # server = IMAPClient(imapServer, use_uid=True, ssl=False);
    # server.login(imapUserame, imapPwd);
    #
    # select_info = server.select_folder('INBOX')
    #
    # print('%d messages in INBOX' % select_info[b'EXISTS'])
    #
    # messages = server.search(['NOT', 'DELETED'])
    # print("%d messages that aren't deleted" % len(messages))
    #
    # print()
    # print("Messages:")
    # response = server.fetch(messages, ['FLAGS', 'RFC822.SIZE'])
    # for msgid, data in response.items():
    #     print('   ID %d: %d bytes, flags=%s' % (msgid,
    #                                             data[b'RFC822.SIZE'],
    #                                             data[b'FLAGS']))



    #
    # conn = imaplib.IMAP4(imapServer,imaplib.IMAP4_PORT);
    # conn.login(imapUserame,imapPwd);
    # # conn.list();
    # conn.select("INBOX");
    # emailTypes, emailDatas = conn.search(None, 'ALL');
    #
    # # 于是如果我想找Essh邮件的话,使用
    # # type, data = conn.search(None, '(SUBJECT "Essh")')
    # # 里面要用一个括号,代表是一个查询条件,可以同时指定多个查询条件,例如FROM xxxx SUBJECT "aaa",注意,命令要用括号罩住(痛苦的尝试)
    # # search第一个参数是charset的意思,填None表示用默认ASCII,
    # msgList = emailDatas[0].split();
    # emailTypes, emailDatas=conn.fetch(msgList[-1],'(RFC822)');
    # msg=email.message_from_string(emailDatas[0][1])
    # content=msg.get_payload(decode=True)


    print("[*] Start download email script");
    start_time = time.time();

    mailaddr = imapUserame;
    password = imapPwd;
    server = imapServer;
    outdir = r"IO全路径";

    # b'(\\NoSelect \\HasChildren) "/" "&UXZO1mWHTvZZOQ-"'

    # with ImapClass(server, mailaddr, password) as imapClient:
    #     folders = imapClient.getMailFolders();
    #     imapClient.downLoadMail(outdir, MailFlagEnum.Unseen);
    #     pass;

    with SmtpClass(smtpServer, smtpUserame, smtpPwd) as smtpClass:
        smtpClass.sendMail(["邮件地址"], "py发送邮件测试 这是标题", "py发送邮件测试 这是文本内容");
        pass;

    # host, port, usr, pwd, use_ssl

    # host, port = imap4(server, 143, mailaddr,password,False);
    # host, port = imap4(server, 993, mailaddr, password, True);
    # create_dir(result_path);
    # protocol_manager(protocol, host, port, mailaddr, password, use_ssl);
    # remove_dir(result_path);
    #
    # end_time = time.time();
    # exec_time = end_time - start_time;
    # print("[*] Finish download email of {0} in {1:.2f}s".format(mailaddr, exec_time));


    pass;


    # #邮件状态设置，新邮件为Unseen
    # #Message statues = 'All,Unseen,Seen,Recent,Answered, Flagged'
    # resp, items = imapServer.search(None, "Unseen")
    # imapServer.close()
    # imapServer.logout()


    # typ, data = M.search(None, 'ALL')
    # for num in data[0].split():
    #    M.store(num, '+FLAGS', '\\Deleted')
    # M.expunge()

    # 附件 邮件发送
    # http://www.cnblogs.com/lonelycatcher/archive/2012/02/09/2343463.html
