from pydantic import BaseModel

class Config(BaseModel):
    #插件命令（默认为glm）
    glm_cmd: str = "glm"

    #你的智谱apikey
    glm_api_key: str = ""

    #聊天记录储存路径，默认为nonebot_plugin_store指定的目录
    glm_history_path: str = ""

    #最大输出的token,0为不限，默认为0
    glm_max_tokens: int = 0

    #使用的模型，默认为glm-3-turbo
    #目前该插件支持的模型有：glm-4、glm-4v、glm-3-turbo
    glm_model: str = "glm-3-turbo"

    #接口地址，一般无需设置，默认为https://open.bigmodel.cn/api/paas/v4/chat/completions
    glm_api_addr: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    #采样温度，控制输出的随机性，必须为正数，取值范围是0.0～1.0，不能等于 0，默认值为 0.5，值越大，会使输出更随机，更具创造性；值越小，输出会更加稳定或确定
    glm_temperature: float = 0.5

    #响应超时时间，默认为60秒
    glm_timeout: int = 60

    #预设，默认为空
    glm_prompt: str = ""

    #ai昵称，默认为空（如果prompt或者nickname有一个为空则无法启用预设）
    glm_nickname: str = ""

    #是否启用ai画图功能，默认为False
    glm_draw: bool = False