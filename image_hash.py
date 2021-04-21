# image_hash.py    11Apr2020  crs
"""  Hash images to reduce rereading/processing 
"""
import re
import os
from PIL import Image, ImageTk

from select_trace import SlTrace
from select_error import SelectError

class ImageHash:
    file_pattern = re.compile(r'<file:(.*)>$')  # in centered text string
    text_pattern = re.compile(r'<text:(.*)>$')  # if default_to_file
    
    def __init__(self, image_dir=None, default_to_files=False):
        """ Setup image file hash
        :image_dir: base level image file directory
                default: ../images
        :default_to_file: interpretation of strings, used only in ancelary functions
                        suchas is_file, is_text
            default: assume files are the form <file:....>
        """
        if image_dir is None:
            image_dir = os.path.join("..", "images")
        self.image_path = os.path.abspath(image_dir)
        self.images_by_key = {}
        self.destroy_function = None
        self.default_to_files = default_to_files
        
    def get_image_path(self):
        """ Get base image path
        """
                
    def get_image(self, key, size=None, photoimage=True):
        """ Get image if one stored
        :key: key to image e.g. file name
        :size: (x,y) scale in pixels
                if present, image file will be loaded and scaled and stored
                default: no resizing is done
        :photoimage: True - return ImageTk.PhotoImage
                    False: return loaded image
                    default: photoimage
        If image not present None will be returned
        :returns: saved image if image present else None
        
        NOTE: image must be independently stored till no longer needed
        Refer to http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm

        """
        if key in self.images_by_key:
            return self.images_by_key[key]
        
        load_image = self.get_load_image(key)
        if load_image is None:
            return None
        
        if size is not None:
            width,height = size
            load_image = load_image.resize((int(width), int(height)), Image.ANTIALIAS)
        if not photoimage:
            return load_image
        
        image = ImageTk.PhotoImage(load_image)
        self.add_image(key, image)
        load_image.close()      # Release resources
        return image

    def get_image_files(self, file_dir=None, name=None):
        """ Get list of image files given name
        :file_dir: file directory
                default: self.image_path
        :name: selection name
            default: all images
        :returns: list of absolute paths to image files
        """
        if file_dir is None:
            file_dir = self.image_path
        if name is not None:
            file_dir = os.path.join(file_dir, name)
        names = os.listdir(file_dir)
        image_files = []
        for name in sorted(names):
            path = os.path.join(file_dir, name)
            if (os.path.exists(path)
                 and not os.path.isdir(path)):
                try:
                    im=Image.open(path)
                    image_files.append(path)
                    im.close() 
                except IOError:
                    SlTrace.lg(f"Not an image file: {path}")
        return image_files   

    def width2size(self, width=None):
        """ Get button size in pixels
        :width: width in characters
            default: guess
        :returns: width, height in pixels
        """
        scale = 5
        if width is None:
            width = 10
        iwidth = int(scale*width)
        iheight = iwidth
        return (iwidth, iheight)

         
    def get_load_image(self, file_path):
        if not re.match(r'.*\.[^.]*$', file_path):
            file_path += ".jpg"
        if not os.path.isabs(file_path):
            file_path = os.path.join("..", "images", file_path)
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            return None
        
        try:
            load_image = Image.open(file_path)
        except:
            raise SelectError(f"Can't open image file {file_path}")
        
        return load_image

    def image_name(self, text, default_to_files=None):
        if self.is_file(text, default_to_files=default_to_files):
            fm = self.file_pattern.match(text)
            if fm is not None:
                return fm.group(1)      # Has pattern e.g. <file:....>
            
            return text

    def is_file(self, text, default_to_files=None):
        """ Check if string indicates a file
        :text: item identifier
        :default_to_files: default interpretation of text
                default: base: self.default_to_files
        :returns: True if file
        """
        if text is None or text == "":
            return False

        if default_to_files is None:
            default_to_files = self.default_to_files
            
        if default_to_files:
            if self.text_pattern.match(text) is not None:
                return False
            return True
        else:
            if self.file_pattern.match(text) is not None:
                return True
            return False

    def is_text(self, text):
        return not self.is_file(text)   # If we add more types, we'll modify
                
    def add_image(self, key, image):
        self.images_by_key[key] = image
        SlTrace.lg(f"image {len(self.images_by_key)}: {key}", "image_add")
        return image

    def name2image_string(self, text_field):
        """ Convert file name to image file string
        :text_field:
        """
        if text_field.startswith("<file:"):
            return text_field       # Already there
        
        return f"<file:{text_field}>"
        
    def clear_cache(self):
        """ Clear the image cache so new calls will check for change
        """
        for key in self.images_by_key:
            image = self.images_by_key[key]
            if self.destroy_function is not None:
                self.destroy_function(image)
            else:
                pass
        self.images_by_key = {}

    def set_image_destroy(self, destroy_function):
        """ Set custom image resource releasing function
        :destroy_function: will be called with image (destroy_function(image)
        Default operation no special releasing action
        """
        self.destroy_function = destroy_function
        
        
