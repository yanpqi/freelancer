# freelancer
FreeLancer是微软出的一款游戏，自由就业的那种意思请绕道。

这个游戏已经很老了，官方早就不维护了，但网上一直有人改各种MOD来玩。最近发现有一个新的地图，地图太大，玩了一天，只玩了一小部分，实在是没精力去一点点的探了，所以发扬程序员精神，写了这个脚本来找出地图中重要的空间位置，包括空间站和跟踪洞的位置。
##使用##
直接运行 python holes.py 就可以了。
##目录介绍##
SYSTEM下是各个星系的配置文件，为了减少上传大小，空间站布局文件已经删除，只留下了XXX.ini的星系空间配置文件。

IONCROSS文件夹下是星系内各种武器装备资料，这部分没有处理，感兴趣的可以自己处理。

GAMEDATA_systems.txt是星系的缩写与全称之间的映射文件。

universe.ini文件里主要提取了各个星系的地图缩放比例，不过有些星系没有缩放比例，导致地图计算误差较大。我猜测存在一个默认的比例（未找到，知道的可以告诉我），自己试了几次，提出一个假想的值，基本上和地图位置比较匹配。
