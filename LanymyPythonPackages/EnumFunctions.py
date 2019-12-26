"""

时间: 2016年01月19日

作者: 

文件: EnumFunctions.py

描述: 枚举扩展方法

其它:

"""
# from enum import Enum;
from LanymyPythonPackages.CustomDecorators import *;
import enum;

class EnumAutoNumber(enum.Enum):
    """
    枚举值自增长 枚举类

    # >>> class Color(AutoNumber):
    # ...     red = ()
    # ...     green = ()
    # ...     blue = ()
    # ...
    # >>> Color.green.value == 2
    # True

    """
    def __new__(cls):
        value = len(cls.__members__) + 1;
        obj = object.__new__(cls);
        obj._value_ = value;
        return obj;
        pass;
    pass;


@accepts(enum.EnumMeta, str)
def getEnumByKey(enumType, keyName):
    """
    :param enumType: 枚举类型
    :param keyName: 要转换枚举项的 名称字符串
    :return:如果没有找到 就返回 此枚举类型的 第一个枚举项
    """
    # if (isinstance(enumType,Enum)):
    #     pass;
    # else:
    #     raise ValueError("参数 enumType 必须是枚举类型");
    #     pass;

    return getattr(enumType, keyName, enumType._member_names_[0]);
    pass;


@accepts(enum.EnumMeta,object)
def getEnumByValue(enumType, theValue):
    """
    :param enumType: 枚举类型
    :param theValue:枚举项的值
    :return:根据值返回对应的枚举项 如果没有 则返回 此枚举类型的 第一个枚举项
    """
    memberNames = enumType._member_names_;
    enumItem = memberNames[0];

    for member in memberNames:
        if (getattr(enumType, member).value == theValue):
            enumItem = member
            pass;
        pass;
    return getattr(enumType, enumItem);
    pass;
