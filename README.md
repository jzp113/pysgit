# pysgit

简介
-----
基于Boost.Python对Sgit的python封装。

环境: Ubuntu16.04 Python2.7

准备:

- `sudo apt install libboost-dev-all g++ make`
- 复制`dev/lib/sgitapi/linux_x64`下so文件到`/lib`， 然后执行`sudo ldconfig`

编译:

- 进入sgitmd目录,执行make
- 进入sgittd目录,执行make


教程参考api目录下py文件.

-----

封装过程参考[xuefu](https://github.com/francinexue/xuefu)项目。