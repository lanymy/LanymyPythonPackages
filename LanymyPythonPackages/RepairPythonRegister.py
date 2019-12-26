"""

时间: 2016年01月12日

作者: 

文件: RepairPythonRegister.py

描述: 修复注册Python对应版本

其它:

"""

import sys;
from winreg import *;


def RepairPythonRegister():
    version = sys.version[:3];
    installPath = sys.prefix;
    regPath = "SOFTWARE\\Python\\Pythoncore\\%s\\" % (version)
    installKey = "InstallPath"
    pythonKey = "PythonPath"
    pythonPath = "%s;%s\\Lib\\;%s\\DLLs\\" % (installPath, installPath, installPath);
    try:
        reg = OpenKey(HKEY_CURRENT_USER, regPath);
    except EnvironmentError as e:
        try:
            reg = CreateKey(HKEY_CURRENT_USER, regPath);
            SetValue(reg, installKey, REG_SZ, installPath);
            SetValue(reg, pythonKey, REG_SZ, pythonPath);
            CloseKey(reg)
        except:
            print("*** Unable to register!");
            return
        print("--- Python", version, "is now registered!");
        return
    if (QueryValue(reg, installKey) == installPath and
                QueryValue(reg, pythonKey) == pythonPath):
        CloseKey(reg)
        print("=== Python", version, "is already registered!");
        return
    CloseKey(reg)
    print("*** Unable to register!");
    print("*** You probably have another Python installation!");
    pass;


if __name__ == "__main__":
    RepairPythonRegister();
    pass;
