// helper.ts

const FIELDNAME = 'CommentTaggerData';
const CHOICES = ['moo', 'zoo'];

var textarea: HTMLTextAreaElement = null;

interface proplist {
    [index: string]: [string, number];
}

function importText(data: proplist, text: string) {
    for (let line of text.split(/\n/)) {
        line = line.trim();
        if (line.length == 0) continue;
        if (line.substr(0,1) == '#') continue;
        let cols = line.split(/,/);
        if (2 <= cols.length) {
            let cid = cols.shift();
            data[cid] = [cols[0], parseInt(cols[1])];
        }
    }
}

function exportText(data: proplist): string {
    let cids = Object.getOwnPropertyNames(data);
    let lines = [] as string[];
    lines.push('#START');
    for (let cid of cids.sort()) {
        let flds = data[cid];
        lines.push(cid+','+flds.join(','));
    }
    lines.push('#END');
    return lines.join('\n');
}

function toArray(coll: NodeListOf<Element>): Element[] {
    let a = [] as Element[];
    for (let i = 0; i < coll.length; i++) {
        a.push(coll[i]);
    }
    return a;
}

function updateHTML(data: proplist) {
    let cids = Object.getOwnPropertyNames(data);
    for (let cid of cids) {
        let flds = data[cid];
        let select = document.getElementById('S'+cid) as HTMLSelectElement;
        if (select !== null) {
            select.value = flds[0];
        }
        let checkbox = document.getElementById('C'+cid) as HTMLInputElement;
        if (checkbox !== null) {
            checkbox.checked = (flds[1] != 0);
        }
    }
}

function saveText() {
    window.localStorage.setItem(FIELDNAME, textarea.value);
}

function initData(): proplist {
    let data: proplist = {};

    function onItemChanged(ev: Event) {
        let e = ev.target as HTMLSelectElement;
        let cid = e.id.substr(1);
        data[cid][0] = e.value;
        textarea.value = exportText(data);
	saveText();
    }

    function onCheckChanged(ev: Event) {
        let e = ev.target as HTMLInputElement;
        let cid = e.id.substr(1);
        data[cid][1] = (e.checked)? 1 : 0;
        textarea.value = exportText(data);
	saveText();
    }

    for (let e of toArray(document.getElementsByClassName('ui'))) {
        let cid = e.id;
        let select = document.createElement('select');
        select.id = 'S'+cid;
        for (let k of CHOICES) {
            let option = document.createElement('option');
            option.setAttribute('value', k);
            option.innerText = k;
            select.appendChild(option);
        }
        let label = document.createElement('label');
        let checkbox = document.createElement('input');
        checkbox.id = 'C'+cid;
        checkbox.setAttribute('type', 'checkbox');
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode('Ung?'));
        e.appendChild(select);
        e.appendChild(document.createTextNode(' '));
        e.appendChild(label);
        select.addEventListener('change', onItemChanged);
        checkbox.addEventListener('change', onCheckChanged);
        data[cid] = [null, 0];
    }
    return data;
}

var curdata: proplist = null;
function run(id: string) {
    function onTextChanged(ev: Event) {
        importText(curdata, textarea.value);
        updateHTML(curdata);
	saveText();
    }
    textarea = document.getElementById(id) as HTMLTextAreaElement;
    textarea.value = window.localStorage.getItem(FIELDNAME);
    textarea.addEventListener('input', onTextChanged);
    curdata = initData();
    importText(curdata, textarea.value);
    updateHTML(curdata);
}
