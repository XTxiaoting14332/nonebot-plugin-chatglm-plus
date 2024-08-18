from html import unescape
from nonebot import on_command, logger, require, get_plugin_config, on_regex,on_keyword,on_message,on_fullmatch
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.rule import to_me
from .config import Config
require("nonebot_plugin_session")
require("nonebot_plugin_localstore")
require("nonebot_plugin_saa")
from nonebot_plugin_session import SessionId, SessionIdType
from pathlib import Path
from nonebot.adapters import Message
import json,os
import jwt
from datetime import datetime, timedelta
import time
import nonebot_plugin_localstore as store
from nonebot.plugin import inherit_supported_adapters
import httpx
from nonebot_plugin_saa import Image





__plugin_meta__ = PluginMetadata(
    name="人性化的ChatGLM",
    description="人性化的ChatGLM插件，支持预设和上下文",
    usage="/glm help查看完整帮助",
    type="application",
    homepage="https://github.com/XTxiaoting14332/nonebot-plugin-chatglm-plus",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_session"),

)




#初始化插件
#读取配置
config = get_plugin_config(Config)
cmd = config.glm_cmd
api_key = config.glm_api_key
max_token = config.glm_max_tokens
base_url = config.glm_api_addr
prompt = config.glm_prompt
nickname = config.glm_nickname
draw_on = config.glm_draw
hisdir = config.glm_history_path
hard_prompt = config.glm_hard_prompt
private = config.glm_private

if config.glm_private == True:
    from nonebot.adapters.onebot.v11 import PrivateMessageEvent,Bot, MessageEvent, GroupMessageEvent
    async def rule_p(event: MessageEvent, bot: Bot) -> bool:
        if isinstance(event, PrivateMessageEvent):
            # 私聊消息一律返回 True
            return True

        return False

if config.glm_at == True:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent,Bot, MessageEvent
    async def rule_g(event: MessageEvent, bot: Bot) -> bool:
        text = event.get_plaintext().strip()
        if isinstance(event, GroupMessageEvent):
            if event.is_tome() and config.glm_at:
                if text:
                    return True
                else:
                    return False

        return False




#聊天记录文件夹
if len(hisdir) == 0:
    history_dir = store.get_data_dir("nonebot_plugin_chatglm_plus")
    log_dir = Path(f"{history_dir}/chatglm-history").absolute()
else:
    if os.path.exists(hisdir):
        log_dir = hisdir
    else:
        logger.warning("找不到设置的路径，将使用默认路径")
        history_dir = store.get_data_dir("nonebot_plugin_chatglm_plus")
        log_dir = Path(f"{history_dir}/chatglm-history").absolute()

log_dir.mkdir(parents=True, exist_ok=True)


#json转义防止爆炸（）
prompt = prompt.replace('\n','\\n')
prompt = prompt.replace('\t','\\t')
prompt = prompt.replace("'","\\'")
prompt = prompt.replace('"','\\"')

#聊天记录实现
#用户输入
def user_in(id, text):
    if os.path.exists(f"{log_dir}/{id}.json"):
        with open(f'{log_dir}/{id}.json', 'a', encoding='utf-8', errors='ignore') as file:
            file.write(',\n{"role": "user", "content": "' + text + '"}')
    else:
        with open(f'{log_dir}/{id}.json', 'w', encoding='utf-8', errors='ignore') as file:
            file.write('{"role": "user", "content": "' + text + '"}')

#AI输出
def ai_out(id, text):
    if os.path.exists(f"{log_dir}/{id}.json"):
        with open(f'{log_dir}/{id}.json', 'a', encoding='utf-8', errors='ignore') as file:
            file.write(',\n{"role": "assistant", "content": "' + text + '"}')
    else:
        with open(f'{log_dir}/{id}.json', 'w', encoding='utf-8', errors='ignore') as file:
            file.write('{"role": "assistant", "content": "' + text + '"}')


#用户识别图片（仅GLM-4V可用）
def user_img(id,url,text):
    if os.path.exists(f"{log_dir}/{id}.json"):
        with open(f'{log_dir}/{id}.json', 'a', encoding='utf-8', errors='ignore') as file:
            file.write(',\n{"role": "user","content": [{"type": "text","text": "'+text+'"},{"type": "image_url","image_url": {"url" : "'+url+'"} }]}')
    else:
        with open(f'{log_dir}/{id}.json', 'w', encoding='utf-8', errors='ignore') as file:
            file.write(',\n{"role": "user","content": [{"type": "text","text": "'+text+'"},{"type": "image_url","image_url": {"url" : "'+url+'"} }]}')



#生成JWT
def generate_token(apikey: str):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("错误的apikey！", e)

    payload = {
        "api_key": id,
        "exp": datetime.utcnow() + timedelta(days=1),
        "timestamp": int(round(time.time() * 1000)),
    }

    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )



if len(api_key) == 0:
    logger.error("[ChatGLM]未正确配置API-Key！！！")
    logger.error("[ChatGLM]未正确配置API-Key！！！")
    logger.error("[ChatGLM]未正确配置API-Key！！！")

if len(prompt) != 0 and len(nickname) != 0:
    logger.info("[ChatGLM]加载预设："+nickname)
    if hard_prompt == True:
        logger.info("硬预设启用")
    rg = True
else:
    logger.info("[ChatGLM]预设未启用")
    rg = False

logger.info("[ChatGLM]使用模型："+config.glm_model)

#指令


ai = on_command(f"{cmd}",aliases={})
reset = on_command(f"{cmd} !reset",aliases={})
ai_img = on_command(f'{cmd} !img',aliases={})
ai_help = on_command(f"{cmd} !help",aliases={})
ai_draw = on_command(f'{cmd} !draw',aliases={})

if config.glm_private == True:
    ai_private = on_message(rule=rule_p)

if config.glm_at == True:
    ai_group = on_message(rule=rule_g)


@ai_help.handle()
async def _handle():
    msg = f"""
    nonebot-plugin-chatglm-plus
    帮助信息：
    /{cmd} 内容 --向ai发送消息
    /{cmd} !reset   --清除当前会话的聊天记录
    /{cmd} !img 图片直链url 文字消息  --向ai发送带有图片的消息(仅glm-4v模型可用)
    /{cmd} !draw 图片描述   --AI画图
    """
    await ai_help.finish(msg)

@ai.handle()
async def _handle(gid: str = SessionId(SessionIdType.GROUP),text: Message = CommandArg()):
    if len(text) != 0:
        text = str(text)
        id = gid.replace(" ","_")
        #对用户输入进行转义防止炸json
        text_r = text.replace("\n","\\n").replace('\t','\\t').replace("'","\\'").replace('"','\\"')
        #读取聊天记录
        if len(api_key) != 0:
            if config.glm_model != 'charglm-3' or config.glm_model != 'emohaa':
                if rg == False:
                    user_in(id,text_r)
                    with open(f'{log_dir}/{id}.json', 'r' ,encoding='utf-8', errors='ignore') as file:
                        history = file.read()
                    history = str(history)
                    history = f"""
                    [
                    {history}
                    ]
                    """
                else:
                    if hard_prompt == False:
                        user_in(id,text_r)
                        with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                            history = file.read()
                        history = str(history)
                        s_prompt = '{"role": "system", "content": "'+prompt+'\\n接下来，请你进入\\"'+nickname+'\\"这个角色与大家对话。请记住你是'+nickname+'，你不能说你是程序或者AI,你是有血有肉、有真实情感的"},'
                        history = f"""
                        [
                        {s_prompt}
                        {history}
                        ]
                        """
                    #硬预设启用
                    else:
                        text_r = text_r + f'({prompt}\\n接下来，请你进入\\"{nickname}\\"这个角色与大家对话。请记住你是{nickname}，你不能说你是程序或者AI,你是有血有肉、有真实情感的)'
                        user_in(id,text_r)
                        with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                            history = file.read()
                        history = str(history)
                        history = f"""
                        [
                        {history}
                        ]
                        """
                try:
                    history = json.loads(history)
                    auth = generate_token(api_key)
                    try:
                        res = str(await req_glm(auth,history))
                        res_raw = res.replace("\n","\\n")
                        ai_out(id,res_raw)
                        await ai.finish(res)
                    except httpx.HTTPError as e:
                        res = f"请求接口出错～\n返回结果：{e}"
                        await ai.finish(res)
                except json.JSONDecodeError:
                    await ai.finish(f"聊天记录似乎炸了？\n请使用/{cmd} !reset 来重置")

            else:
                user_in(id,text_r)
                with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                    history = file.read()
                history = str(history)
                history = f"""
                [
                {history}
                ]
                """
            try:
                history = json.loads(history)
                auth = generate_token(api_key)
                try:
                    res = str(await req_glm_char(auth,history))
                    res_raw = res.replace("\n","\\n")
                    ai_out(id,res_raw)
                    await ai.finish(res)
                except httpx.HTTPError as e:
                    res = f"请求接口出错～\n返回结果：{e}"
                    await ai.finish(res)
            except json.JSONDecodeError:
                    await ai.finish(f"聊天记录似乎炸了？\n请使用/{cmd} !reset 来重置")

        else:
            await ai.finish("API-Key未正确配置！")

    else:
        await ai.finish(f"消息不能为空\n可使用/{cmd} !help 命令查看帮助")


if config.glm_private == True:
    @ai_private.handle()
    async def _handle(event: PrivateMessageEvent,id: str = SessionId(SessionIdType.GROUP)):
        if private == True:
            text = unescape(event.get_plaintext().strip())
            id = id.replace(" ","_")
            #对用户输入进行转义防止炸json
            text_r = text.replace("\n","\\n").replace('\t','\\t').replace("'","\\'").replace('"','\\"')
            #读取聊天记录
            if len(api_key) != 0:
                if config.glm_model != 'charglm-3' or config.glm_model != 'emohaa':
                    if rg == False:
                        user_in(id,text_r)
                        with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                            history = file.read()
                        history = str(history)
                        history = f"""
                        [
                        {history}
                        ]
                        """
                    else:
                        if hard_prompt == False:
                            user_in(id,text_r)
                            with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                                history = file.read()
                            history = str(history)
                            s_prompt = '{"role": "system", "content": "'+prompt+'\\n接下来，请你进入\\"'+nickname+'\\"这个角色与大家对话。请记住你是'+nickname+'，你不能说你是程序或者AI,你是有血有肉、有真实情感的"},'
                            history = f"""
                            [
                            {s_prompt}
                            {history}
                            ]
                            """
                        #硬预设启用
                        else:
                            text_r = text_r + f'({prompt}\\n接下来，请你进入\\"{nickname}\\"这个角色与大家对话。请记住你是{nickname}，你不能说你是程序或者AI,你是有血有肉、有真实情感的)'
                            user_in(id,text_r)
                            with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                                history = file.read()
                            history = str(history)
                            history = f"""
                            [
                            {history}
                            ]
                            """
                    try:
                        history = json.loads(history)
                        auth = generate_token(api_key)
                        try:
                            res = str(await req_glm(auth,history))
                            res_raw = res.replace("\n","\\n")
                            ai_out(id,res_raw)
                            await ai_private.finish(res)
                        except httpx.HTTPError as e:
                            res = f"请求接口出错～\n返回结果：{e}"
                            await ai_private.finish(res)
                    except json.JSONDecodeError:
                        await ai_private.finish(f"聊天记录似乎炸了？\n请使用/{cmd} !reset 来重置")

                else:
                    user_in(id,text_r)
                    with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                        history = file.read()
                    history = str(history)
                    history = f"""
                    [
                    {history}
                    ]
                    """
                try:
                    history = json.loads(history)
                    auth = generate_token(api_key)
                    try:
                        res = str(await req_glm_char(auth,history))
                        res_raw = res.replace("\n","\\n")
                        ai_out(id,res_raw)
                        await ai.finish(res)
                    except httpx.HTTPError as e:
                        res = f"请求接口出错～\n返回结果：{e}"
                        await ai_private.finish(res)
                except json.JSONDecodeError:
                        await ai_private.finish(f"聊天记录似乎炸了？\n请使用/{cmd} !reset 来重置")

            else:
                await ai_private.finish("API-Key未正确配置！")






#at
if config.glm_at == True:
    @ai_group.handle()
    async def _handle(event: GroupMessageEvent,gid: str = SessionId(SessionIdType.GROUP)):
        text = unescape(event.get_plaintext().strip())
        #对用户输入进行转义防止炸json
        text_r = text.replace("\n","\\n").replace('\t','\\t').replace("'","\\'").replace('"','\\"')
        if config.glm_at == True:
            id = gid.replace(" ","_")
            if len(api_key) != 0:
                if config.glm_model != 'charglm-3' or config.glm_model != 'emohaa':
                    if rg == False:
                        user_in(id,text_r)
                        with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                            history = file.read()
                        history = str(history)
                        history = f"""
                        [
                        {history}
                        ]
                        """
                    else:
                        if hard_prompt == False:
                            user_in(id,text_r)
                            with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                                history = file.read()
                            history = str(history)
                            s_prompt = '{"role": "system", "content": "'+prompt+'\\n接下来，请你进入\\"'+nickname+'\\"这个角色与大家对话。请记住你是'+nickname+'，你不能说你是程序或者AI,你是有血有肉、有真实情感的"},'
                            history = f"""
                            [
                            {s_prompt}
                            {history}
                            ]
                            """
                        #硬预设启用
                        else:
                            text_r = text_r + f'({prompt}\\n接下来，请你进入\\"{nickname}\\"这个角色与大家对话。请记住你是{nickname}，你不能说你是程序或者AI,你是有血有肉、有真实情感的)'
                            user_in(id,text_r)
                            with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                                history = file.read()
                            history = str(history)
                            history = f"""
                            [
                            {history}
                            ]
                            """
                    try:
                        history = json.loads(history)
                        auth = generate_token(api_key)
                        try:
                            res = str(await req_glm(auth,history))
                            res_raw = res.replace("\n","\\n")
                            ai_out(id,res_raw)
                            await ai_group.finish(res)
                        except httpx.HTTPError as e:
                            res = f"请求接口出错～\n返回结果：{e}"
                            await ai_group.finish(res)
                    except json.JSONDecodeError:
                        await ai_group.finish(f"聊天记录似乎炸了？\n请使用/{cmd} !reset 来重置")

                else:   
                    user_in(id,text_r)
                    with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                        history = file.read()
                    history = str(history)
                    history = f"""
                    [
                    {history}
                    ]
                    """
                try:
                    history = json.loads(history)
                    auth = generate_token(api_key)
                    try:
                        res = str(await req_glm_char(auth,history))
                        res_raw = res.replace("\n","\\n")
                        ai_out(id,res_raw)
                        await ai_group.finish(res)
                    except httpx.HTTPError as e:
                        res = f"请求接口出错～\n返回结果：{e}"
                        await ai_group.finish(res)
                except json.JSONDecodeError:
                        await ai_group.finish(f"聊天记录似乎炸了？\n请使用/{cmd} !reset 来重置")

            else:
                await ai_group.finish("API-Key未正确配置！")







@ai_img.handle()
async def _handle(gid: str = SessionId(SessionIdType.GROUP),args: Message = CommandArg()):
    id = gid.replace(" ","_")
    args = str(args)
    argl = args.split()
    if config.glm_model == "glm-4v":
        if len(argl) != 0:
            url = argl[0]
            text = argl[1]
            text_r = text.replace("\n","\\n")
            #读取聊天记录
            if len(api_key) != 0:
                if rg == False:
                    user_img(id,url,text_r)
                    with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                        history = file.read()
                    history = str(history)
                    history = f"""
                    [
                    {history}
                    ]
                    """
                else:
                    if hard_prompt == False:
                        user_img(id,url,text_r)
                        with open(f'{log_dir}/{id}.json', 'r', encoding='utf-8', errors='ignore') as file:
                            history = file.read()
                        history = str(history)
                        s_prompt = '{"role": "system", "content": "'+prompt+'\\n接下来，请你进入\\"'+nickname+'\\"这个角色与大家对话。请记住你是'+nickname+'，你不能说你是程序或者AI,你是有血有肉、有真实情感的"},'
                        history = f"""
                        [
                        {s_prompt}
                        {history}
                        ]
                        """
                    else:
                        text_r = text_r + f'({prompt}\\n接下来，请你进入\\"{nickname}\\"这个角色与大家对话。请记住你是{nickname}，你不能说你是程序或者AI,你是有血有肉、有真实情感的)'
                        user_img(id,url,text_r)
                        with open(f'{log_dir}/{id}.json', 'r') as file:
                            history = file.read()
                        history = str(history)
                        history = f"""
                        [
                        {history}
                        ]
                        """
                history = json.loads(history)
                auth = generate_token(api_key)
                try:
                    res = str(await req_glm(auth,history))
                    res_raw = res.replace("\n","\\n")
                    ai_out(id,res_raw)
                    await ai_img.finish(res)
                except httpx.HTTPError as e:
                    res = f"请求接口出错～\n返回结果：{e}"
                    await ai_img.finish(res)
            else:
                await ai_img.finish("API-Key未正确配置！")

        else:
            await ai_img.finish(f"参数不足！\n用法：/{cmd} !img [图片直链url] [你的文本消息]")
    else:
        await ai_img.finish(f"目前使用的模型为{config.glm_model}，不支持图片识别，请使用glm-4v模型")


#AI画图
@ai_draw.handle()
async def _handle(arg: Message = CommandArg()):
    arg = str(arg)
    if draw_on == True:
        try:
            auth = generate_token(api_key)
            await ai_draw.send("正在画图，请稍等")
            img_url = str(await req_draw(auth,arg))
            await Image(img_url).finish()
        except httpx.HTTPError as e:
            await ai_draw.finish(f'貌似出错了~\n{e}')
    else:
        await ai_draw.finish("未开启AI画图功能")



@reset.handle()
async def _handle(gid: str = SessionId(SessionIdType.GROUP)):
    id = gid.replace(" ","_")
    try:
        os.remove(f"{log_dir}/{id}.json")
        await reset.finish("已清除聊天记录")
    except FileNotFoundError:
        await reset.finish("当前还没有会话哦！")




#异步请求AI
async def req_glm(auth_token, usr_message):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    if max_token == 0:
        data = {
            "model": config.glm_model,
            "temperature": config.glm_temperature,
            "messages": usr_message
        }
    else:
        data = {
            "model": config.glm_model,
            "max_tokens": max_token,
            "temperature": config.glm_temperature,
            "messages": usr_message
        }

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=config.glm_timeout, write=20, pool=30)) as client:
        res = await client.post(base_url, headers=headers, json=data)
        res = res.json()
    try:
        res_raw = res['choices'][0]['message']['content']
    except Exception as e:
        res_raw = res
    return res_raw


#charglm-3响应
async def req_glm_char(auth_token, usr_message):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    if max_token == 0:
        data = {
            "model": config.glm_model,
            "temperature": config.glm_temperature,
            "messages": usr_message,
            "meta": {
                "bot_info": prompt,
                "bot_name": nickname
            }
        }
    else:
        data = {
            "model": config.glm_model,
            "max_tokens": max_token,
            "temperature": config.glm_temperature,
            "messages": usr_message,
            "meta": {
                "bot_info": prompt,
                "bot_name": nickname
            }
        }

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=config.glm_timeout, write=20, pool=30)) as client:
        res = await client.post(base_url, headers=headers, json=data)
        res = res.json()
    try:
        res_raw = res['choices'][0]['message']['content']
    except Exception as e:
        res_raw = res
    return res_raw



#异步请求AI画图
async def req_draw(auth_token,arg):
    draw_url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    data = {
    "model": "cogview-3",
    "prompt": arg
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10, read=config.glm_timeout, write=20, pool=30)) as client:
        res = await client.post(draw_url, headers=headers, json=data)
        res = res.json()
    try:
        res_raw = res['data'][0]['url']
    except Exception as e:
        res_raw = res
    return res_raw
