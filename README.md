# GfxHealthCheck

- error context
- all invalid - None

- check lspci output
- check packages
- check glxinfo installed
- check glxinfo output
- check mesa libs installed
- check 

# requirements
- python 3.5
- cmake 3.7
- gcc 4.8.1

# build
```bash
mkdir build && cd build && cmake .. && make
```

# usage
after build 
```bash
python3 gfxhealthcheck.py
```