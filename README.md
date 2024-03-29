![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-cord?style=for-the-badge) ![GitHub](https://img.shields.io/github/license/nekooooooooo/salty-dream-bot?style=for-the-badge) ![GitHub last commit](https://img.shields.io/github/last-commit/nekooooooooo/salty-dream-bot?style=for-the-badge)

# Salty Dream Bot
A simple, unoptimized locally run Stable Diffusion discord bot

![](https://raw.githubusercontent.com/nekooooooooo/nekooooooooo.github.io/master/pics/preview_dream_bot_2.png)

This was mostly made for my friend's private server.
I won't be maintaining this repo that much (like most of my repos) but I'll try my best to finish everything on the [to do](#to-do) list

# Project may or may not be abandoned, please use [Kilvoctu's Aiya Bot](https://github.com/Kilvoctu/aiyabot) instead.

It has better implementation of Automatic1111's WebUI API and more features that I have yet to add on mine, also actively being maintained.


## Setup

- Set up [AUTOMATIC1111's Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- Run the Web UI with the api command line argument inside (`COMMANDLINE_ARGS=--api`)
- Clone this repository
- `pip install -r requirements.txt`
- Create a .env inside the repo

```dotenv
# .env
TOKEN = bot token here
```

## Features

### Basic txt2img
![](https://user-images.githubusercontent.com/69033860/204470547-5c8959f7-339a-4994-9b6f-1b3f049ddb68.gif)
- Negative Prompts
- Image orientation/aspect ratio (square, landscape, portrait)
- Image size presets (small, normal, large)
- Seed
- Samplers
- Hypernetworks

### Interrogate using CLIP and DeepDanbooru
![](https://raw.githubusercontent.com/nekooooooooo/nekooooooooo.github.io/master/pics/preview_dream_bot_interrogate.png)

## Optional .env variables:

```dotenv
URL = set URL

# will move default prompts to configurable per-server config when it's implemented

DEFAULTPROMPT = default prompt for generations (not that useful added it in for more customizability)
NEGATIVEPROMPT = default negative prompt for generations
```


## Credits
- AUTOMATIC1111, and all the contributors of the [Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- Kilvoctu, for the [API guide](https://github.com/AUTOMATIC1111/stable-diffusion-webui/discussions/3734#discussioncomment-3976954) and their implementation of the API with [Aiya Bot](https://github.com/Kilvoctu/aiyabot)
- mix1009, for their [python API client library](https://github.com/mix1009/sdwebuiapi)

## To Do
- [ ] Optimize code
- [ ] Save prompts into styles
- [ ] Optional custom width/height
- [ ] Stats command
- [ ] AIO setup/run
- [ ] API Auth

### In progress (ordered by priority)
- [ ] Add comments for better code readability (mostly for myself)
- [x] Refactor code
    - [ ] Subclasses
    - [x] Cogs
- [ ] Extras
    - [ ] Upscaling
- [ ] Queues
- [x] Display progress
    - [ ] Remove dirty fix
- [ ] Model/checkpoint
- [x] Hypernetwork
    - [x] Hypernetwork strenght
- [ ] Config
    - [ ] Default model/checkpoint swapping
    - [ ] Default hypernetwork swapping
- [ ] Remove test code comments
- [ ] Locally save images
- [ ] Add restore faces option
- [ ] Error handling
- [x] img2img
    - [ ] Refactor maybe
- [ ] Batch size
    - [ ] Image grid

### Completed
- [x] Interrupt
    - [x] Only author can interrupt
- [x] Samplers
- [x] Interrogate with CLIP/DeepDanbooru
- [x] PNG info
