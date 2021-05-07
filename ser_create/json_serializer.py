import json
from inspect import stack
from .my_load import load as ld
from .my_dump import dump as dp


class JsonSerializer:

    one_ld = True
    
    def loads(self, string):
        if self.one_ld:
            stack_step = 1
        else:
            stack_step = 2
        self.one_ld = True

        ld_dict = json.loads(string)
        obj = ld(ld_dict, stack()[stack_step][0].f_globals)
        return obj


    def dumps(self, obj):
        dump_dict = dp(obj)
        return json.dumps(dump_dict, indent=4)
        

    def load(self, fp):
        fp.seek(0)
        string = fp.read()
        self.one_ld = False
        return self.loads(string)  
        

    def dump(self, obj, fp):
        string = self.dumps(obj)
        fp.write(string)
        fp.flush()


    def __str__(self):
        return 'JSON serializer'
