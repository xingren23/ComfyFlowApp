# ComfyFlowApp
Load Comfy workflow as Web App in seconds

## 简介
ComfyFlowApp 是ComfyUI的扩展工具，你可以将ComfyUI工作流转换为WebApp应用，并分享给其他用户访问。

工作流开发者使用ComfyUI开发工作流，通过组合ComfyUI节点以及自定义扩展节点，ComfyUI工作流可以完成复杂的工作，如生成用户写真、电商产品换背景等，解决很多工作场景的实际需求。
但对普通用户来说，构建工作流复杂度高、需要花费大量精力，ComfyFlowApp简化了分享和使用工作流的方式，工作流开发者方便地分享给其他用户，其他用户不需要关心工作流内部细节，就可以使用工作流。

关注本项目，获取最新动态。

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/comfyflow)

### 快速开始
- Linux & Mac
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量，设置你的ComfyUI服务地址，ComfyUI服务地址默认为 127.0.0.1:8188
export COMFYUI_SERVER_ADDR=127.0.0.1:8188

# 启动 ComfyFlowApp
sh bin/start.sh
```

- Windows
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量，设置你的ComfyUI服务地址，ComfyUI服务地址默认为 127.0.0.1:8188
set COMFYUI_SERVER_ADDR=127.0.0.1:8188

# 启动 ComfyFlowApp
./bin/run.bat
```

### 如何开发一个ComfyFlowApp？

- 工作流开发, 在ComfyUI中开发工作流，参考[ComfyUI](https://github.com/comfyanonymous/ComfyUI)
![图1](docs/images/comfy-workflow.png)

- 工作流管理，在 Workspace 管理工作流，包括创建及编辑应用、预览应用、发布应用，以及启动和停止应用等；
![图2](docs/images/comfy-workspace.png)

    - (1)创建应用，上传工作流图片，配置应用参数，生成WebApp应用；
![图3](docs/images/comfy-upload-app.png)

    - (2)预览应用，预览WebApp应用，检查web应用是否正常；
![图4](docs/images/comfy-preview-app.png)

    - (3)发布应用，发布WebApp应用，生成WebApp应用链接；
![图5](docs/images/comfy-release-app.png)

    - (4)启动、停止应用，启动WebApp应用，访问WebApp应用链接；
![图6](docs/images/comfy-app.png)

## 相关项目
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

## 联系我们
ComfyWorkflowApp 项目还处于早期阶段，如果您有任何问题或建议，欢迎通过以下方式联系我们：

- [GitHub Issues](https://github.com/xingren23/ComfyWorkflowApp/issues)

- WeChat: 如果微信群二维码过期，请添加我的微信号：xingren23，备注“ComfyFlowApp”，我拉你进群。

![alt-text-1](docs/images/WechatGroup.jpg "title-1") ![alt-text-2](docs/images/wechat-xingren23.jpg "title-2")