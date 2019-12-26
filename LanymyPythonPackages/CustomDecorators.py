"""

时间: 2016年01月08日

作者:

文件: CustomDecorators.py

描述: 自定义装饰器

其它:

"""

import inspect;
import os;


def accepts(*argsTypes, **keyWordArgsTypes):
    """
    形参 参数类型 限制装饰器
    调用例子如下
    # >>> @accepts(str, arg2=int)
    # ... def f(arg1, arg2=None):
    # ...     pass
    # ...
    #
    #
    # >>> f('foo')
    # >>> f('foo', arg2=3)
    # >>> f()
    # TypeError: f() takes at least 1 argument (0 given)
    # >>> f('foo', 'bar')
    # TypeError: f() takes at most 1 non-keyword arguments (2 given)
    # >>> f('foo', arg2='bar')
    # TypeError: Parameter 'bar' is not int
    # >>> f('foo', arg3='bar')
    # TypeError: Unexpected keyword argument 'arg3' for f()
    #
    #
    # >>> class A(object):
    # ...     pass
    # ...
    # >>> class B(object):
    # ...     @accepts(object, (str, unicode))
    # ...     def f(self, s):
    # ...         pass
    # ...
    # ...     @accepts(object, A)
    # ...     def g(self, a):
    # ...         pass
    #
    # >>>
    # >>> b = B()
    # >>> b.f(u'foo')
    # >>> b.f('foo')
    # >>> b.g(A())
    # >>> b.g(B())
    # TypeError: Parameter '<__main__.B object at 0x902466c>' is not A
    """

    def wrapper(func):
        def wrapped(*args, **keyWordArgs):
            if len(args) > len(argsTypes):
                raise TypeError("%s() takes at most %s non-keyword arguments (%s given)" % (
                    func.__name__, len(argsTypes), len(args)))
            argsPairs = zip(args, argsTypes)
            for k, v in keyWordArgs.items():
                if k not in keyWordArgsTypes:
                    raise TypeError("Unexpected keyword argument '%s' for %s()" % (k, func.__name__))
                argsPairs.append((v, keyWordArgsTypes[k]))
            for param, expected in argsPairs:
                if param is not None and not isinstance(param, expected):
                    raise TypeError("Parameter '%s' is not %s" % (param, expected.__name__))
            return func(*args, **keyWordArgs)

        return wrapped

    return wrapper

    pass;


def returns(rType):
    """
    返回参数类型定义

    # >>> @returns(int)
    # ... @accepts(str, arg2=int)
    # ... def f(arg1, arg2=None):
    # ...     return 0
    # ...
    :param rType: 返回参数的数据类型
    """

    def wrapper(f):
        def wrapped(*args, **kwargs):
            result = f(*args, **kwargs)
            if not isinstance(result, rType):
                raise TypeError("return value %r does not match %s" % (result, rType))
            return result

        return wrapped

    return wrapper

    pass;


def singleInstance(func):
    """
    单例模式装饰器

    # @singleton
    # class MyClass4(object):
    # a = 1
    # def __init__(self, x=0):
    #     self.x = x

    """
    instances = {}

    def _singleton(*args, **kw):
        if func not in instances:
            instances[func] = func(*args, **kw)
        return instances[func]

    return _singleton

    pass;


def privateInitCall(func):
    """
    类内部实例化装饰器
    使用此装饰器 标记的 __init__ 类初始化方法  为类私有方法
    只有类自己可以创建类实例
    外部必须调用类内部提供的实例化方法 才能 成功获取该类的实例
    此装饰器 只在 类的__init__ 类初始化方法上 标记才会生效
    修饰其它一切方法 则自动忽略跳过
    """

    def _PrivateCall(*args, **kw):

        if (func.__name__ != "__init__"):
            return func(*args, **kw);
            pass;

        # 调用方名称
        callName = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0];
        # 方法基类名称
        callFuncBaseName = str(func).split()[1].split(".")[0];

        if (callName != callFuncBaseName):
            # 如果不是类内部自己调用方法 则抛出异常
            raise SyntaxError("方法 {0} 只能在 {1} 内部调用,外部不可调用!".format(func.__name__, callFuncBaseName));
            pass;

        return func(*args, **kw);
        pass;

    return _PrivateCall;
    pass;
