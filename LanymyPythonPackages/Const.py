"""

时间: 2016年01月07日

作者:

文件: Const.py

描述: 常量类

其它:

"""

import sys


class Const(object):
    class ConstError(TypeError):
        pass;

    def __setattr__(self, key, value):

        # if self.__dict__.has_key(key):
        if key in self.__dict__:
            raise self.ConstError("Changing const.{0}".format(key));
        else:
            self.__dict__[key] = value

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.key
        else:
            return None


sys.modules[__name__] = Const()

# if __name__ == '__main__':
#     Const.AAA = 123;
#     print(Const.AAA);
#     pass;
