# Plugins Marketplace

## Installing from the marketplace

First search in the [Github Topics](https://github.com/topics/jarvis-plugin) the features basket that you wish to install: search for the keyword "jarvis-plugin". Alternatively, you can list top availables plugins with the plugin *market find*.

Once you know the specific "user/features_basket_name", install it via the plugin: *market buy github_user/basket_name*.

## Creating your basket to the marketplace

Create a Github repository and tag it with "jarvis-plugin". Create plugins following the official [guide](PLUGINS.md) as to how to build plugins. We suggest the following schema in the Github repo:

- your_plugin.py
- requirements.txt
- LICENSE
- README.md
- .gitignore

However the *market buy* only needs the _your_plugin.py_

The whole repo will be saved in the folder _marketplace/_, and your plugin will be installed and read for use when you restart Jarvis.

## Plugin functions

* market find: search Github Topics for plugin baskets to _buy_.

* market buy: install a basket of plugins via 'user/basket_name'.
