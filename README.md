1) Create Environment
2) Set your IDE environment to use it (e.g., VSCode)
   (Linux) CTR+SHIFT+P -> Python Select Interpreter
3) Install python dependencies
   pip install paho-mqtt requests
4) Install Bluesky (suggest: Fedora)

   pip install .
   pip install RTree
   pip install "bluesky-simulator[full]"
5) Run Bluesky
   cd bluesky
   python BlueSky.py

#if does not work
python BlueSky_pygame.py
7) Change the configuration file to start in the desired place (/home/kabart/github/cyber-argus/bluesky/settings.cfg)
start_location = 'SBRJ'
