<div align="center">
  <a href="https://nonebot.dev/store/plugins/"><img src="image/logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
<div align="center">

# nonebot-plugin-chatglm-plus
</div>
_✨ 人性化的ChatGLM插件，使用智谱API✨_<br>


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/XTxiaoting14332/nonebot-plugin-chatglm-plus.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-chatglm-plus">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-chatglm-plus.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>



## 📖 介绍

人性化的ChatGLM插件，使用智谱API<br>


## 💪 支持的适配器
``OneBot v11``<br>
``OneBot v12``<br>
``Console``<br>
``Kaiheila``<br>
``Telegram``<br>
``Feishu``<br>
``RedProtocol``<br>
``Discord``<br>
``QQ``<br>
``Satori``<br>
``DoDo``<br>

## 🥵 环境要求
Python >=3.8<br>
Nonebot >=2.2.0<br>
<br>
## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令安装

    nb plugin install nonebot-plugin-chatglm-plus

</details>

<details>
<summary>pip安装</summary>

    pip install nonebot-plugin-chatglm-plus

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_chatglm_plus"]
</details>
<details>
<summary>Github下载</summary>
手动克隆本仓库或直接下载压缩包，将里面的nonebot_plugin_chatglm-plus文件夹复制到src/plugins中,并安装以下依赖

    httpx  PyJWT nonebot-plugin-session

</details>


</details><br>


## 🔧配置项
### 必填项

```
#智谱清言的API Key
glm_api_key = 
```

### 非必填项

```
#插件命令（默认为glm）
glm_cmd = glm

#最大输出的token,0为不限，默认为0
glm_max_tokens = 0

#聊天记录储存路径，默认为nonebot_plugin_store指定的目录
glm_history_path = ""


#使用的模型，默认为glm-3-turbo
#目前该插件支持的模型有：glm-4、glm-4v、glm-3-turbo
glm_model = glm-3-turbo

#接口地址，一般无需设置，默认为https://open.bigmodel.cn/api/paas/v4/chat/completions
glm_api_addr = https://open.bigmodel.cn/api/paas/v4/chat/completions

#采样温度，控制输出的随机性，必须为正数，取值范围是0.0～1.0，不能等于 0，默认值为 0.5，值越大，会使输出更随机，更具创造性；值越小，输出会更加稳定或确定
glm_temperature = 0.5

#响应超时时间，默认为60秒
glm_timeout = 60

#预设，默认为空
glm_prompt = ""

#ai昵称，默认为空（如果prompt或者nickname有一个为空则无法启用预设）
glm_nickname = ""

#是否启用ai画图功能，默认为False
glm_draw = False
```


<br>

## 🎉 使用
### 指令表（需要加上命令前缀，默认为/）
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| glm | 所有人 | 否 | ~ | 向ai发送消息 |
| glm !reset| 所有人 | 否 | ~ | 清除当前会话的聊天记录 |
| glm !img 图片url 文本消息 | 所有人 | 否 | ~ | 向ai发送带有图片的消息(仅glm-4v模型可用) |
| glm !draw 图片要求 | 所有人 | 否 | ~ | AI画图 |
| glm !help| 所有人 | 否 | ~ | 获取插件帮助 |
