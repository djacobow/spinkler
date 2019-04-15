
var pageLog = function(s) {
    gebi('errors').innerText += s;
};

var setValve = function(i,what = 'set') {
    data = {
        "pattern": 0x1 << i,
	"action": what,
    }
    PostJS('/vctrl',data,(err,res) => {
        if (err) return pageLog(err);
        showSet(res.current);
    });
}

var showSet = function(vdata) {
    for (var i=0;i<16;i++) {
        var i_on = (0x1 << i) & vdata;
        var selem = gebi('status_' + i);
        selem.innerText = i_on ? 'is ON' : 'is OFF';
    }
};


var createButtons = function(target, total) {
    var vtable = cr('table');
    for (var i=0;i<total;i++) {
        var td0 = cr('td',null,'Valve ' + (i+1).toString());
        var tr = cr('tr');
        var td1 = cr('td');
        var b_on = cr('button');
        b_on.id = 'btn_on_' + i;
        b_on.innerText = "On";
        b_on.addEventListener('click',(ev) => {
            setValve(parseInt(ev.target.id.replace('btn_on_','')),'setbits');
	});
        td1.appendChild(b_on);

        var td2 = cr('td');
        var b_off = cr('button');
        b_off.id = 'btn_off_' + i;
        b_off.innerText = "Off";
        b_off.addEventListener('click',(ev) => {
            setValve(parseInt(ev.target.id.replace('btn_off_','')),'clrbits');
	});
        td2.appendChild(b_off);


        var td3 = cr('td');
        td3.id = "status_" + i;

        tr.appendChild(td0);
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        vtable.appendChild(tr);
    }
    target.appendChild(vtable);
    GetJS('/vctrl',(err,res) => {
        if (err) return pageLog(err);
        showSet(res.current);
    });

};

var valve_init = function() {
    var vdiv = gebi('valve_stuff');
    createButtons(vdiv,16);
};

