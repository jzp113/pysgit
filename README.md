#pysgit

简介
-----
基于Boost.Python对Sgit的python封装。

环境: Linux Python2.7

准备:

- 安装boost, g++
- `cd dev/lib/sgitapi/linux_x64 & sudo cp *.so /lib & sudo ldconfig`

编译:
    进入sgitmd目录,执行make

教程参考api目录下py文件

TODO:

- 优化行情接口
- 封装交易接口

封装过程参考[xuefu](https://github.com/francinexue/xuefu)项目。