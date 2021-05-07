import pickle
from inspect import stack
from .my_load import load as ld
from .my_dump import dump as dp

class PickleSerializer:
    
    one_ld = True
    
    def loads(self, bin_string):
        if self.one_ld:
            stack_step = 1
        else:
            stack_step = 2
        self.one_ld = True
        
        ld_dict = pickle.loads(bin_string)
        obj = ld(ld_dict, stack()[stack_step][0].f_globals)
        return obj


    def dumps(self, obj):
        dump_dict = dp(obj)
        return pickle.dumps(dump_dict)


    def load(self, fp):
        fp.seek(0)
        bin_string = fp.read()
        self.one_ld = False
        return self.loads(bin_string)  


    def dump(self, obj, fp):
        bin_string = self.dumps(obj)
        fp.write(bin_string)
        fp.flush()


    def __str__(self):
        return 'Pickle serializer'

