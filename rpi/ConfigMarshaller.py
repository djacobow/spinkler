import json

class ConfigMarshaller(object):
    def __init__(self,base_fn):

        with open(base_fn, 'r') as f:
            self._config = json.load(f)

        self._paths = {}
        for changeable in self._config['config_ui_changeables']:
            path = changeable.get('path',None)
            if path:
                self._paths[path] = changeable

        with open(self._config['user_config_fn'], 'r') as f:
            overrides = json.load(f);
            for override in overrides:
                self.setV(override['path'],override['value'])
            
    def getConfig(self):
        return self._config

    def getV(self, changeable):
        path = changeable.get('path',None)
        if path:
            chunks = path.split('/')
            v = self._config
            for chunk in chunks:
                v = v.get(chunk,None)
            return v
        return None

    def setV(self, path, value):
        if self._paths.get(path,None) is not None:
            chunks = path.split('/')
            t = self._config
            for i in range(len(chunks)-1):
                t = t[chunks[i]]
            t[chunks[-1]] = value

    def dcopy(self, i):
        return { k:v for (k,v) in i.items() }

    def mergeChanges(self,indata):
        print(indata)
        for datum in indata:
            path = datum.get('path',None)
            if path and path in self._paths:
                self.setV(path,datum.get('value',None))

    def saveConfig(self):
        rv = []
        for changeable in self._config['config_ui_changeables']:
            v = self.getV(changeable);
            path = changeable.get('path',None)
            if path:
                rv.append({'path':path,'value':v});
        with open(self._config['user_config_fn'], 'w') as ofh:
            ofh.write(json.dumps(rv,sort_keys=True,indent=2))


    def getValues(self):
        rv = []
        for changeable in self._config['config_ui_changeables']:
            v = self.getV(changeable)
            o = self.dcopy(changeable)
            o['value'] = v
            rv.append(o)
        return rv



if __name__ == '__main__':
    cm = ConfigMarshaller('./base_config.json')
    cm.saveConfig()

