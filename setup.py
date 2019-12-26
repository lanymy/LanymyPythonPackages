"""

时间: 2016年01月18日

作者: 

文件: setup.py

描述: 

其它:

"""




if (__name__ == "__main__"):
    from setuptools import setup, find_packages

    setup(
            name="LanymyPythonPackages",
            version="1.0.0",
            packages=find_packages(),
            # package_dir = {'':'src'},
            author='lanymy',
            author_email='',
            description='Python通用扩展包',
            # install_requires=[],
    )
    pass;


#打包 参数 bdist_egg
# egg文件卸载
# 以python2.6版本为例，egg文件一般安装在/usr/local/lib/python2.6/dist-packages/目录下，
# 该目录下还有一个easy-install.pth文件，用于存放安装的egg信息。:

# 一般第三方的组件都是以egg文件的方式存在的，安装egg文件需要先安装setuptools工具，下载地址：https://pypi.python.org/pypi/setuptools/，下载完成后双击msvc-build-launcher编译即可。
#
# 查看安装是否成功：在你的Python安装路径下（我的是C:\\Python27）进入Scripts文件夹，查看是否有easy_install.exe文件，有就安装成功了！
#
# 安装egg文件时，打开CMD，依次键入：
#
# cd  \d c:\Python27\Scripts
#
# easy_install  zope.interface-4.1.2-py2.7-win32.egg
# //调用easy_install  安装你的EGG文件


# 到http://peak.telecommunity.com/DevCenter/EasyInstall下载ez_setup.py,然后运行它，它会下载你安装的python版本所对应的setuptools.它会把easy_install.exe安装到$PYTHON-HOME/Scripts下，安装好后，你运行easy_install xxxx.egg就可以了。
