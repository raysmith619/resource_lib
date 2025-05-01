# image_hash.py    11Apr2020  crs
"""  Hash images to reduce rereading/processing
Support image hash by image by size (widthxheight),
        by Image (0) or PhotoImage(1)
        
"""
import re
import os
from PIL import Image, ImageTk

from select_trace import SlTrace
from select_error import SelectError

class ImageInfo:
    """ Image information
    """
    def __init__(self, key, base_image=None,
                 photoimage=True):
        """ Setup image info based on key
        :key: unique key e.g. file name/path
        :base_image: base Image
        :photoimage: True PhotoImage, False Image
                default: PhotoImage
        """
        self.key = key
        self.base_image = base_image
        self.scaled_images = {}    # Hash of scaled images,
                                    # by (x,y, photoimage)
        self.photoimage = photoimage    # Default

    def get_scaled_image(self, size=None,
                         photoimage=True):
        """ retrieve image, possibly scaled, possibly converted to photoimage
        from database If existing scale or photoimage is not present,
        the opperation is done and the result is stored before
        returning
        :size: (x,y) scaled dimensions None no scaling and no photo
        :photoimage: True converted to PhotoImage
        :returns: processed image
        """
        ik = (size, photoimage)
        if ik in self.scaled_images:
            return self.scaled_images[ik]
        
        if size is not None:
            i_width,i_height = size
            image = self.base_image.resize((int(i_width),
                             int(i_height)), Image.LANCZOS)
        else:
            image = self.base_image     # Unscaled
        if photoimage:
            image = ImageTk.PhotoImage(image)
        self.scaled_images[ik] = image      # Save scaled/photo
        return image
        
        
    
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
        image_path = os.path.abspath(image_dir)
        self.image_path = image_path
        self.image_infos_by_key = {}    # Image information
        self.images_by_key = {}
        self.destroy_function = None
        self.default_to_files = default_to_files
        
    def get_image_path(self):
        """ Get base image path
        """
                
    def get_image(self, key, size=None, photoimage=True):
        """ Get image if one stored
        Image original is stored
        If scaled, the scaled image is stored by size, photoimage
        On subsequent requests by size, the scaled image is returned
        :key: key to image e.g. file name
        :size: (x,y) scale in pixels
                if present, loaded image will be scaled and stored
                default: no resizing is done
        :photoimage: True - return ImageTk.PhotoImage
                    False: return loaded image
                    default: photoimage
        If image not present None will be returned
        :returns: None if no such key
                scaled/converted image if possible
                
        
        NOTE: image must be independently stored till no longer needed
        Refer to http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm

        """
        if key not in self.image_infos_by_key:
            load_image = self.get_load_image(key)
            if load_image is None:
                return None     # No image to be found
            else:
                self.add_image(key, image=load_image)
        
        image = self.get_scaled_image(key, size=size,
                                       photoimage=photoimage)
        return image

    def add_image(self, key, image):
        """ Add base image to database
        Replaces previous image, if any
        :key: image key, e.g. file name
        :image: base image loaded from file
        """
        self.image_infos_by_key[key] = ImageInfo(key, base_image=image)

    def get_image_info(self, key):
        if key in self.image_infos_by_key:
            return self.image_infos_by_key[key]
        
        return None

    def get_scaled_image(self, key, size=None, photoimage=True):
        """ retrieve image, possibly scaled, possibly converted to photoimage
        from database If existing scale or photoimage is not present,
        the opperation is done and the result is stored before
        returning
        :key: image key, e.g. file name
        :size: (x,y) scaled dimensions None no scaling
        :photoimage: True converted to PhotoImage
        :returns: processed image
        """
        image_info = self.get_image_info(key)
        if image_info is None:
            return None
        
        image = image_info.get_scaled_image(size=size, photoimage=photoimage)
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
        if not os.path.isdir(file_dir):
            SlTrace.lg(f"Ignoring non-directory path:{file_dir}")
            return []
        
        names = os.listdir(file_dir)
        image_files = []
        for name in sorted(names):
            if name.endswith(".txt"):
                continue
            
            path = os.path.join(file_dir, name)
            if (os.path.exists(path)
                 and not os.path.isdir(path)):
                try:
                    im=Image.open(path)
                    image_files.append(path)
                    im.close() 
                except IOError:
                    SlTrace.lg(f"Ignoring non-image file path:{path}")
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
        base_path = file_path
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.image_path, file_path)
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
        
        
if __name__ == "__main__":
    import os
    from tkinter import Tk
    
    root = Tk()
    
    image_dir = os.path.join("..", "images", "miscellaneous")
    image_dir = os.path.abspath(image_dir)
    SlTrace.lg(f"image_dir: {image_dir}")
    base_dir = os.path.basename(image_dir)
    SlTrace.lg(f"base_dir: {base_dir}")
    ih = ImageHash(image_dir=image_dir)
    image_files = ih.get_image_files()
    ist = {}  # by (size,photomiage)
    for image_file in image_files:
        bf = os.path.basename(image_file)
        for width in [100, 200, 300]:
            size = (width,width)
            pi = False
            ###ist[size, pi] = 
            imbase1 = ih.get_image(image_file, size=size,
                                photoimage=pi)
            pi = True
            ist[size, pi] = imphoto1 = ih.get_image(image_file, size=size,
                                photoimage=pi)
            pi = False
            ###ist[size, pi] = 
            imbase2 = ih.get_image(image_file, size=size,
                                photoimage=pi)
            pi = True
            ist[size, pi] = imphoto2 = ih.get_image(image_file, size=size,
                                photoimage=pi)
            SlTrace.lg(f"imbase1: {bf} {size} {imbase1}")
            SlTrace.lg(f"imphoto1: {bf} {size} {imphoto1}")
            SlTrace.lg(f"imbase2: {bf} {size} {imbase1}")
            SlTrace.lg(f"imphoto2: {bf} {size} {imphoto2}")
            SlTrace.lg()
        

    