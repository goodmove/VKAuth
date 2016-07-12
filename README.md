# VKAuth

## Authorization on VK for humans

VKAuth is a lightweight flexible module for you to authenticate a session for your applicaton, which uses VK API.
This module is written in python 3.5 and uses `requests` library as an essentinal dependency

## Usage

1. `import` the module into your project
2. Create new class instance with appropriate parameters. Call `authorize()` method to start connection and get `access_token`. Don't forget to call `close()` to close connection and finish session
```
vk = VKAuth(['photos'], '123123', '5.52')
vk.authorize()

# your code goes here

vk.close()
```

## Features

- Works great with two-factor authentication: set `two_factor_auth=True` and provide the `security_code` at initialization time or enter when prompted
- Provide email and passwords at authentication time or be prompted to enter them
- Exception handling and responsivness
- Ease of use

## Dependencies

- [requests](https://github.com/kennethreitz/requests/) module 
- HTMLParser

If you find bugs or have suggestions about improving the module, don't hesitate to contact me.
