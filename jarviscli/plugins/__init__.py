"""
                +---------+         +----------+
                | Jarvis  |-------->| packages |
                +---------+         +----------+
                 |   |   |                   |
    +------------+   |   +-----------        +--+
    |                |              |           |
    v                v              v           v
 +---------+    +----------+   +--------+   +---------------------+        For this row,
 | Plugins |    | Frontend |   | Parser |   | InformationProvider |    <-- there are multiple
 +---------+    +----------+   +--------+   +---------------------+        providers
   |
   |
   v
 +-----------+
 | utilities |
 +-----------+


 * Jarvis is the "main" class and bundles:
     - Plugins: A 'command' the user can call
     - Frontend: Displays and/or receives input to/from user
     - Parser: Language Parser to handle user input
     - Packages: Various code to provider the "Jarvis API"
                 used by the plugins
* Utilities consists of help functions used mainly by plugins
"""


