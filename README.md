![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-cord?style=for-the-badge) ![GitHub last commit](https://img.shields.io/github/last-commit/nekooooooooo/salty-dream-bot?style=for-the-badge)

# Salty Dream Bot
A simple, unoptimized locally run Stable Diffusion discord bot

<img src="https://raw.githubusercontent.com/nekooooooooo/nekooooooooo.github.io/master/pics/preview_dream_bot.png">

This was mostly made for my friend's private server.
I won't be maintaining this repo that much (like most of my repos) but I'll try my best to finish everything on the [to do](#to-do) list

I recommend using [Kilvoctu's Aiya Bot](https://github.com/Kilvoctu/aiyabot) instead. It has better implementation of Automatic1111's WebUI API and more features that I have yet to add on mine, also actively being maintained.

## Setup

- Set up [AUTOMATIC1111's Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- Run the Web UI with the api command line argument inside (`COMMANDLINE_ARGS=--api`)
- Clone this repository
- Create a .env inside the repo

```dotenv
# .env
TOKEN = bot token here
```

## Features

- Basic txt2img
- Negative Prompts
- Image orientation/aspect ratio (square, landscape, portrait)
- Image size presets (small, normal, large)
- Seed

## Optional .env variables:

```dotenv
URL = set URL

# will move default prompts to configurable per-server config when it's implemented

DEFAULTPROMPT = default prompt for generations (not that useful added it in for more customizability)
NEGATIVEPROMPT = default negative prompt for generations
```

## To Do

- [ ] Refactor code
    - [ ] Subclasses
    - [ ] Cogs
- [ ] Optimize code
- [ ] Per-server config
- [ ] Save prompts into styles
- [ ] Extras
    - [ ] Upscaling
- [ ] Model/checkpoint swapping
    - [ ] Hypernetwork swapping
        - [ ] Hypernetwork strenght
- [ ] Interrogate/DeepDanbooru
- [ ] Optional custom width/height
- [ ] Stats command
- [ ] AIO setup/run
- [ ] Batch size
    - [ ] Image grid

### In progress (ordered by priority)
- [ ] Add comments for better code readability (mostly for myself)
- [ ] Queues
- [ ] Remove test code comments
- [ ] Locally save images
- [ ] Add restore faces option
- [ ] Error handling
- [ ] PNG info
- [ ] img2img
- [ ] Display progress
- [ ] API Auth

### Completed
- [x] Interrupt
    - [x] Only author can interrupt
- [x] Samplers
