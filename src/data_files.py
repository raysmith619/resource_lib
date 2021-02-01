# data_files.py    31Jan2021
"""
Provide uniform access to programm data files
particularly image files grouped in create_directories
for games, e.g., keyboard_draw.py

"""
import os 

from image_hash import ImageHash

from select_trace import SlTrace
from select_list import SelectList
from image_hash import ImageHash

class DataFileGroup:
    """ File info, especially for image file
    """
    def __init__(self, group_name, data_dir, file_type="image", image=None,
                 image_hash=None, image_files=[],
                 select_image_hash=None, select_image_files=None):
        """ Setup file
        :group_name: DataFiles name
        :data_dir: directory for files
        :file_type: data file type
                default: "image"
        :image_hash: image hash ImageHash
        :image_files: image files else None
        :select_image_hash: image SelectList hash
        :select_image_files: image files else None
        """
        self.group_name = group_name
        self.data_dir = data_dir
        self.file_type = file_type
        self.image_hash = image_hash
        self.image_files = image_files
        self.select_image_hash = select_image_hash
        self.select_image_files = select_image_files
        self.set_file_index(-1)     # Next is 0

    def set_file_index(self, index=0):
        self.file_index = index
    
    def inc_file_index(self, inc=1):
        """ Increment file index, returning new index
            resets index to 0 if >= len
            resets index to len(self.image_files)-1 if < 0
        :inc: amount of increment
        """
        
        self.file_index += inc
        if self.file_index >= len(self.image_files):
            self.file_index = 0
        elif self.file_index < 0:
            self.file_index = len(self.image_files)-1 
        return self.file_index

    def get_file(self, inc=0):
        """ Get next file
        :inc: increment index
                default: 0 - no chage
        """
        index = self.inc_file_index(inc)
        return self.image_files[index] 

    def get_image_files(self):
        """ Get image files
        """
        return self.image_files
    
class DataFiles:
    """ Collection of information to facilitate the efficient access
    to a group of files in a directory especially a group of image files
    """
    def __init__(self, data_dir=None, file_type="image",
                 select_list=True):
        """ Setup file access
        :name: unique name of group, used to access group
        :data_dir: default base file directory
                default: ../images 
        :file_type: default type of files
                default: image - image files (loadable by Pillow(PIL))
        :select_list:    Provide SelectList support for files
                Currently only for file_type == "image"
                default: True
        """
        self.data_file_groups = {} 
        if data_dir is None:
            src_dir = os.path.dirname(os.path.abspath(__file__))
            SlTrace.lg(f'src_dir:{src_dir}')
            prj_dir = os.path.dirname(src_dir)
            SlTrace.lg(f'prj_dir:{prj_dir}')
            file_dir = os.path.join(prj_dir, "images")
        self.data_dir = data_dir
        self.file_type = file_type

    def add_group(self, name, group_dir=None, file_type=None,
                 select_list=True):
        """ Add data file group
        :name: group name
        :group_dir: directory holding files
                    default: self.data_dir/name
        :file_type: file type
                    default: "image"
        """
        if group_dir is None:
            group_dir = os.path.join(self.data_dir, name)
        self.group_dir = group_dir
        if file_type is None:
            file_type = self.file_type
        self.file_type = file_type
        image_hash = None
        image_files = None
        select_image_hash = None
        select_image_files = None
        if file_type == "image":
            """ Setup image hash for selection possibility 
            via SelectList """
            SlTrace.lg(f"image_dir:{group_dir}")
            image_hash = ImageHash(image_dir=group_dir)
            image_files = image_hash.get_image_files()
            if select_list:
                select_image_hash = ImageHash(image_dir=self.group_dir)
                select_image_files = select_image_hash.get_image_files()
        
        data_file_group = DataFileGroup(name, data_dir=group_dir,
                                        file_type=file_type,
                                        image_hash=image_hash,
                                        image_files=image_files,
                                        select_image_hash=select_image_hash,
                                        select_image_files=select_image_files)    
        self.data_file_groups[name] = data_file_group

    def get_group(self, name):
        """ Get data file group
        :name: group name
        :returns: group (DataFileGroup)
                    Error if not present
        """
        return self.data_file_groups[name]

    def get_groups(self):
        """ Get all group names, sorted
        """
        return sorted(list(self.data_file_groups))
    
if __name__ == "__main__":
        import os 
        
        SlTrace.lg(f"Self test of {os.path.basename(__file__)}")
        
        x0 = 300
        y0 = 400
        width = 200
        height = 400
        SlTrace.lg(f"x0={x0}, y0={y0}, width={width}, height={height}", "select_list")
  
        image_dir = os.path.join("..", "images")
        image_dir = os.path.abspath(image_dir)
        dfl = DataFiles(data_dir=image_dir)
        image_sub_dirs = os.listdir(image_dir)
        image_dirs = []
        for im_sub_dir in image_sub_dirs:
            image_dirs.append(os.path.join(image_dir, im_sub_dir))

        for image_dir in image_dirs:
            name = os.path.basename(image_dir)
            
            dfl.add_group(name, group_dir=image_dir)

        SlTrace.lg("Testing each data files group")           
        for im_dir in image_dirs:
            name = os.path.basename(im_dir)

            SlTrace.lg(f"Testing group {name}")
            dfg = dfl.get_group(name)
            app = SelectList(items=dfg.select_image_files, default_to_files=True,
                             title=f"{name} Image Buttons",
                             position=(x0, y0), size=(width, height))
            selected_field = app.get_selected(return_text=True)
            SlTrace.lg(f"image_image: selected_field:{selected_field}")
            if selected_field is not None:
                image = dfg.image_hash.get_image(selected_field)
                SlTrace.lg(f"selected image: {image}")
        
                        