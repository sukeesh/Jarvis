# Plugins Marketplace

## Installing from the marketplace

First search in the [Github Topics](https://github.com/topics/jarvis-plugins) the features basket that you wish to install: search for the keyword "jarvis-plugins". Alternatively, you can list availables plugins with the plugin *market searc*.

Once you know the specific "user/features_basket_name", install it via the plugin: *market buy user/features_basket_name*.

**Warnings** If there is any conflict of name it will throw an error. Be careful with trying to install packages if similar names.

## Creating your basket to the marketplace

Create a Github repository and tag it with "jarvis-plugins". Create plugins following the official [guide](PLUGINS.md) as to how to build plugins. Add your code in it following the exact same schema from the Jarvis main branch. The *market buy* plugin will install all the additional codes in comparison with your current local version of Jarvis.

The only special case is the file _requirements.txt_ in the _installer_ folder. It will inscribe new lines as compared to your current version.

**Warnings** If there is any conflict of name it will throw an error. Be careful with trying to install packages if similar names.

## Plugin functions

* market search: search Github Topics for plugin baskets to _buy_.

* market buy: install a basket of plugins via 'user/basket_name'.
