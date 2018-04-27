import platform

if platform.system() == "Darwin":
    def null_fill():
        return "systemTransparent"
else:
    def null_fill():
        return "white"
