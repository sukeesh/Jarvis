#!/bin/sh
cd $(dirname $0)
cd ..
source env/bin/activate
cd jarviscli
pydocmd simple CmdInterpreter CmdInterpreter.JarvisAPI+ > ../doc/API.md
pydocmd simple tests tests.PluginTest+ tests.MockHistory+ > ../doc/TEST_API.md
