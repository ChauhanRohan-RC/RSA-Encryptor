from ctypes import windll, byref, create_unicode_buffer, create_string_buffer

# constants used in AddFontResourceEx function
FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20


def load_font(font_path, private=True, enumerable=False):
    """
    Makes fonts located in file "font_path" available to the font system.
    private  if True, other processes cannot see this font, and this font
             will be unloaded when the process dies
    enumerable  if True, this font will appear when enumerating fonts
    see http://msdn2.microsoft.com/en-us/library/ms533937.aspx
    """

    if isinstance(font_path, str):
        path_buf = create_unicode_buffer(font_path)
        call = windll.gdi32.AddFontResourceExW
    elif isinstance(font_path, bytes):
        path_buf = create_string_buffer(font_path)
        call = windll.gdi32.AddFontResourceExA
    else:
        raise TypeError('font path must be a str or unicode')

    flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
    num_fonts_added = call(byref(path_buf), flags, 0)
    return bool(num_fonts_added)


def unload_font(font_path, private=True, enumerable=False):
    """
    Unloads the fonts in the specified file.
    see http://msdn2.microsoft.com/en-us/library/ms533925.aspx
    """

    if isinstance(font_path, bytes):
        path_buf = create_string_buffer(font_path)
        call = windll.gdi32.RemoveFontResourceExA
    elif isinstance(font_path, str):
        path_buf = create_unicode_buffer(font_path)
        call = windll.gdi32.RemoveFontResourceExW
    else:
        raise TypeError('font path must be a str or unicode')

    flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
    return bool(call(byref(path_buf), flags, 0))
