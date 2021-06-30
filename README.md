# windows+python3环境

> **Step 1: 安装python3**  
```
安装过的可以直接跳过
```

> **Step 2: 本地执行**  
```
(1) 使用cmd(或Terminal)进入项目所在目录folder_peek-master
> cd xxxxxxxx\folder_peek-master
(2) 安装依赖，这里使用阿里镜像
xxxxxxxx\folder_peek-master> pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
(3) 将待解析的文件夹xxxx（例如"文件页数统计"）复制到data文件夹中
(4) 执行命令，"xxxx"即刚才复制的文件夹名，例如"文件页数统计"
xxxxxxxx\folder_peek-master> python peek.py xxxx
```