""" helper functions for configuring logging locations.
"""


import platform

def get_location():
    log_dir = "./"

    if "Linux" in platform.platform():
        return log_dir

    try:
        import ctypes
        from ctypes import wintypes, windll
        CSIDL_COMMON_APPDATA = 35
        _SHGetFolderPath = windll.shell32.SHGetFolderPathW
        _SHGetFolderPath.argtypes = [wintypes.HWND,
                                    ctypes.c_int,
                                    wintypes.HANDLE,
                                    wintypes.DWORD, wintypes.LPCWSTR]

        path_buf = wintypes.create_unicode_buffer(wintypes.MAX_PATH)
        result = _SHGetFolderPath(0, CSIDL_COMMON_APPDATA, 0, 0, path_buf)
        log_dir = path_buf.value
    except:
        log.exception("Problem assigning log directory")

    return(log_dir)
