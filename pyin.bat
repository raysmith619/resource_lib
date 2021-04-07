pyinstaller cli.py ^
 --name=keyboard_draw ^
 --paths ../../resource_lib/src ^
 --add-data keyboard_draw_hello.txt;. ^
 --add-data hello_family.txt;. ^
 --add-data ../../resource_lib/images;./images
