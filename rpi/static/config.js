/* jshint esversion:6 */


var pageLog = function(e) {
    gebi('errors').innerText += e;
};

var ConfigManager = function() {
    this._cfgdata = [];

    ConfigManager.prototype.getCalendarList = function(target, curr_id = null) {
        GetJS('/calendars',(err,data) => {
            if (err) {
                return pageLog(err);
            }

            removeChildren(target);
            data.forEach((item) => {
                var option = cr('option',null,item.summary);
                option.value = item.id;
                target.add(option);
                if (curr_id && (item.id == curr_id)) option.selected = 'selected';
            });
        });
    };

    ConfigManager.prototype.storeBack = function(ev) {
        var rv = [];
        this._cfgdata.forEach((datum) => {
            cfg_id = datum.id || null;
            elem = datum.elem || null;
            if (cfg_id && elem) {
                console.log(datum);
                value = gebi(cfg_id).value;
                if (datum.type == 'bool') {
                    console.log('bool',value);
                    value = value == 'true' ? true : false;
                    console.log('new bool',value);
                } else if (datum.type == 'integer') {
                    value = parseInt(value);
                }
                path = datum.path;
                rv.push({value:value,path:path});
            }
        });
        PostJS('/config',rv,(err,res) => {
            if (err) return pageLog(err);
        });
    };

    ConfigManager.prototype.populate = function() {
        GetJS('/config',(err,data) => {
            if (err) return pageLog(err);
            var table = cr('table');
            this._cfgdata = data;
            count = 0;
            data.forEach((datum) => {
                var path = datum.path || null;
                var value = datum.value || null;
                var type = datum.type || 'string';
                var descr = datum.descr || '';
                var cfg_id = "cfg_item_" + count.toString();
                datum.id = cfg_id;
                count += 1;
                var tr = cr('tr');
                var td0, td1, td2;
                switch (type) {
                    case 'rule':
                        td0 = cr('td');
                        td0.appendChild(cr('hr'));
                        td0.colSpan = 2;
                        tr.appendChild(td0);
                        break;
                    case 'heading':
                        td0 = cr('td',null,descr);
                        td0.colSpan = 2;
                        tr.appendChild(td0);
                        break;
                    case 'bool':
                        td0 = cr('td',null,descr);
                        td1 = cr('td');
                        tf0 = cr('select');
                        datum.elem = tf0;
                        tf0.addEventListener('change',(ev) => {
                            this.storeBack(ev);
                        });
                        tf0.id = cfg_id;
                        tt = cr('option',null,'true');
                        tt.value = true;
                        ff = cr('option',null,'false');
                        ff.value = false;
                        tf0.add(tt);
                        tf0.add(ff);
                        if (value) {
                            tt.selected = 'selected';
                        } else {
                            ff.selected = 'selected';
                        }
                        tr.appendChild(td0);
                        tr.appendChild(td1);
                        td1.appendChild(tf0);
                        break;
                    case 'calendar_selector':
                        td0 = cr('td',null,descr);
                        td1 = cr('td');
                        csel0 = cr('select');
                        csel0.id = cfg_id;
                        datum.elem = csel0;
                        csel0.addEventListener('change',(ev) => {
                            this.storeBack(ev);
                        });
                        this.getCalendarList(csel0,value);
                        td1.appendChild(csel0);
                        tr.appendChild(td0);
                        tr.appendChild(td1);
                        break;
                    case 'string':
                        td0 = cr('td',null,descr);
                        td1 = cr('td');
                        inp0 = cr('input');
                        inp0.id = cfg_id;
                        inp0.type = 'text';
                        inp0.value = value;
                        datum.elem = inp0;
                        inp0.addEventListener('change',(ev) => {
                            this.storeBack(ev);
                        });
                        td1.appendChild(inp0);
                        tr.appendChild(td0);
                        tr.appendChild(td1);
                        break;
                    case 'integer':
                        td0 = cr('td',null,descr);
                        td1 = cr('td');
                        inp0 = cr('input');
                        inp0.id = cfg_id;
                        inp0.type = 'number';
                        inp0.step = 1;
                        if (datum.min) inp0.min = datum.min;
                        if (datum.max) inp0.max = datum.max;
                        inp0.value = value;
                        datum.elem = inp0;
                        inp0.addEventListener('change',(ev) => {
                            this.storeBack(ev);
                        });
                        td1.appendChild(inp0);
                        tr.appendChild(td0);
                        tr.appendChild(td1);
                        break;
                }
                table.appendChild(tr);
            });
            gebi('config_stuff').appendChild(table);
        });
    };
};




var config_init = function() { 
    var cm = new ConfigManager();
    cm.populate();
};
