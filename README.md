# VKAuth

## Authorization on VK for humans

VKAuth is a lightweight flexible module for you to authenticate a session for your application, which uses VK API.
This module is written in `python 3.5` and uses `requests` library as an essential dependency

## Usage

1. `import` the module into your project
2. Create new class instance with appropriate parameters. Call `authorize()` method to start connection and get `access_token`. Don't forget to call `close()` to close the session.

Class parameters:

1. Required
  - `permissions`: `list` - permissions your app wants to get
  - `app_id`: `string` - id of your app
  - `api_v`: `string` - VK API version
2. Optional
  - `email`: `string` - email to log in with | default: `None`
  - `pswd`: `string` - password for account with `email` | default: `None`
  - `two_factor_auth`: `bool` - whether to use two-factor authentication or not | default: `False`
  - `security_code`: `string` - code to log in with in case of two-factor auth. | default: `None`
  - `auto_access`: `bool` - whether to allow to grant access to `permissions` automatically (needed only once) | default: `True`
```
vk = VKAuth(['photos'], '123123', '5.52')
vk.authorize()

access_token = vk.access_token

# your code goes here

vk.close()
```

## Features

- Works great with two-factor authentication: set `two_factor_auth=True` and provide the `security_code` at initialization time or enter when prompted
- Provide email and passwords at authentication time or be prompted to enter them
- Exception handling and responsiveness
- Ease of use

## Dependencies

- [requests](https://github.com/kennethreitz/requests/) module
- HTMLParser

If you find bugs or have suggestions about improving the module, don't hesitate to contact me.
