
# 📌 Welcome to ComfyFlowApp

ComfyFlowApp is a tool to help you develop AI webapp from ComfyUI workflow and share to others.

English | [简体中文](./README_zh-CN.md)

## 📌 What is ComfyFlowApp?
ComfyFlowApp is an extension tool for ComfyUI, making it easy to create a user-friendly application from a ComfyUI workflow and lowering the barrier to using ComfyUI.

As shown in the images below, you can develop a web application from the workflow like "portrait retouching"

![图1](docs/images/demo-workflow.png)
![图2](docs/images/demo-webapp.png)

### Why You Need ComfyFlowApp?
If you want to generate an image using AI tools, you can choose MidJourney, DALL-E3, Fairfly (Adobe), or similar tools. These tools allow anyone to generate a beautiful image based on prompts. However, if you need more control over the generated results, like dressing a model in specific clothing, these tools may not suffice. Additionally, if your scenario has specific copyright requirements for images, you can use the open-source Stable Diffusion to build an AI image processing application. You have the choice of Stable-Diffusion-WebUI or ComfyUI, with WebUI being simple to use and having a rich plugin ecosystem for various processing needs. On the other hand, ComfyUI has a higher learning curve but offers more flexible workflow customization, allowing you to develop workflows for a wide range of scenarios.

If you need to share workflows developed in ComfyUI with other users, ComfyFlowApp can significantly lower the barrier for others to use your workflows:

- Users don't need to understand the principles of AI generation models.
- Users don't need to know the tuning parameters of various AI models.
- Users don't need to understand where to download models.
- Users don't need to know how to set up ComfyUI workflows.
- Users don't need to understand Python installation requirements.

ComfyFlowApp helps application developers make these complexities transparent to users, who can use it like any other regular application.

**In summary, if you want to share workflows developed in ComfyUI with other users, choosing ComfyFlowApp is the right choice.**

### Typical Use Cases
1) Studio or Internal Business Collaboration

In scenarios where a studio or internal business needs collaborative work division and not everyone needs to understand AI, various models, and workflow construction, a typical collaboration scenario involves one or a few developers building an AI application within ComfyUI, achieving satisfactory results, and saving the workflow. Then, developers use ComfyFlowApp's Creator tool to convert the workflow into a web application, hiding irrelevant fine-tuning parameters, making the application simple and easy to use. Developers can then share the application's address with other users within the studio or the company, who can access the deployed application through the shared address.

2) Professional Creators or Teams, Developing and Sharing Applications with a Wider Audience

Professional creators or teams can use ComfyUI tools to develop valuable applications, but the usability of ComfyUI may be too high for the normal user. By using ComfyFlowApp to transform a workflow into an application suitable for a broader audience, developers can create more value. This process typically involves developers creating a workflow in ComfyUI, achieving satisfactory results, and saving the workflow. Developers then use ComfyFlowApp's Creator tool to convert the workflow into a web application, hiding irrelevant fine-tuning parameters, and making the application easy to use. After that, developers can publish the application in an app store, allowing other users to discover and download the application and run it locally.


**Follow the repo to get the latest updates.**

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/comfyflow)

### 📌 Quick Start
- Linux
```bash
# download project
git clone https://github.com/xingren23/ComfyFlowApp

# Creator for developer
cd ComfyFlowApp/creator
# install requirements
pip install -r requirements.txt
# configure environment variables, defaulut ComfyUI server address is 127.0.0.1:8188
export COMFYUI_SERVER_ADDR=127.0.0.1:8188
# start Creator
sh bin/start.sh

# Studio for user
cd ComfyFlowApp/studio
# update submodule ComfyUI
git submodule update --init --recursive
# install requirements
pip install -r requirements.txt
# start Studio
sh bin/start.sh
```

- Windows
You can download the integrated package, extract it, and run it directly without the need to install dependencies.
```base
# Creator for developer
click creator-run.bat to start

# Studio for user
click studio-run.bat to start
```

       
### 📌 Related Projects
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

### 📌 Contact Us
- [GitHub Issues](https://github.com/xingren23/ComfyWorkflowApp/issues)

- WeChat: if wegroup is expired, you could add xingren23，comment “ComfyFlowApp”，I will invite you to the group.

![alt-text-1](docs/images/WechatGroup.jpg "title-1") ![alt-text-2](docs/images/wechat-xingren23.jpg "title-2")