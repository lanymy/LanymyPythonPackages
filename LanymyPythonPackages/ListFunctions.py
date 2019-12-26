"""

时间: 2016年01月15日

作者: 

文件: ListFunctions.py

描述: 列表辅助方法

其它:

"""

from LanymyPythonPackages.CustomDecorators import *;


@accepts(list)
def RemoveAllEmptyItem(listSource):
    """
    清除列表中的空元素
    :param listSource:
    :return:
    """

    resultList = [];

    for x in listSource:
        if(x.strip()):
            resultList.append(x);
            pass;
        pass;

    return resultList;

    pass;