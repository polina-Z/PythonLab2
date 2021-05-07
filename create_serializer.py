from ser_create.json_serializer import JsonSerializer
from ser_create.pickle_serializer import PickleSerializer
from ser_create.yaml_serializer import YamlSerializer
from ser_create.toml_serializer import TomlSerializer
    

def create_serializer(ser_lang):
    if ser_lang == 'json':
        return JsonSerializer()
    if ser_lang == 'pickle':
        return PickleSerializer()
    if ser_lang == 'toml':
        return TomlSerializer()
    if ser_lang == 'yaml':
        return YamlSerializer()
    raise TypeError('Invalid serializer name1')
    
    
def create_serializer_file(ser_lang, in_file=""):
     
    if in_file == "":
        return create_serializer(ser_lang)
    else: 
        file_ext = in_file.rpartition(".")[2]
        if file_ext == ser_lang:
            return create_serializer(ser_lang)
        else:
            return create_serializer(file_ext)
    raise TypeError('Invalid serializer name2')
