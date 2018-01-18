// helper.ts

const FIELDNAME = 'CommentTaggerData';
const CHOICES = [
    'm:Meta Info.', 'o:Value Desc.',
    'a:Precondition', 'p:Postcondition',
    't:Type/Enum/Iface', 'i:Instruction', 'g:Guide',
    'c:Comment Out', 'v:Visual Cue',
    'd:Directive', 'u:Uncategorized'
];

var textarea: HTMLTextAreaElement = null;

class Item {
    ctype: string = '';
    ung: boolean = false;
    updated: number = 0;

    load(cols: string[]) {
        this.ctype = cols[0];
        this.ung = (cols[1] == 'true');
        this.updated = parseInt(cols[2]);
    }

    save() {
        return this.ctype+','+this.ung+','+this.updated;
    }
}

interface ItemList {
    [index: string]: Item;
}

function importText(data: ItemList, text: string) {
    for (let line of text.split(/\n/)) {
        line = line.trim();
        if (line.length == 0) continue;
        if (line.substr(0,1) == '#') continue;
        let cols = line.split(/,/);
        if (2 <= cols.length) {
            let cid = cols.shift();
            let item = new Item();
            item.load(cols);
            data[cid] = item;
        }
    }
}

function exportText(data: ItemList): string {
    let cids = Object.getOwnPropertyNames(data);
    let lines = [] as string[];
    lines.push('#START');
    for (let cid of cids.sort()) {
        let item = data[cid];
        lines.push(cid+','+item.save());
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

function updateHTML(data: ItemList) {
    let cids = Object.getOwnPropertyNames(data);
    for (let cid of cids) {
        let item = data[cid];
        let select = document.getElementById('S'+cid) as HTMLSelectElement;
        if (select !== null) {
            select.value = item.ctype;
        }
        let checkbox = document.getElementById('C'+cid) as HTMLInputElement;
        if (checkbox !== null) {
            checkbox.checked = item.ung;
        }
    }
}

function saveText() {
    if (window.localStorage) {
        window.localStorage.setItem(FIELDNAME, textarea.value);
    }
}

function initData(): ItemList {
    let data: ItemList = {};

    function onCtypeChanged(ev: Event) {
        let e = ev.target as HTMLSelectElement;
        let cid = e.id.substr(1);
        let item = data[cid];
        item.ctype = e.value;
        item.updated = Date.now();
        textarea.value = exportText(data);
	saveText();
    }

    function onUngChanged(ev: Event) {
        let e = ev.target as HTMLInputElement;
        let cid = e.id.substr(1);
        let item = data[cid];
        item.ung = e.checked;
        item.updated = Date.now();
        textarea.value = exportText(data);
	saveText();
    }

    for (let e of toArray(document.getElementsByClassName('ui'))) {
        let cid = e.id;
        let select = document.createElement('select');
        select.id = 'S'+cid;
        for (let k of CHOICES) {
            let i = k.indexOf(':');
            let option = document.createElement('option');
            let v = k.substr(0, i);
            option.setAttribute('value', v);
            option.innerText = v+')'+k.substr(i+1);
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
        select.addEventListener('change', onCtypeChanged);
        checkbox.addEventListener('change', onUngChanged);
        data[cid] = new Item();
    }
    return data;
}

var curdata: ItemList = null;
function run(id: string) {
    function onTextChanged(ev: Event) {
        importText(curdata, textarea.value);
        updateHTML(curdata);
	saveText();
    }
    textarea = document.getElementById(id) as HTMLTextAreaElement;
    if (window.localStorage) {
        textarea.value = window.localStorage.getItem(FIELDNAME);
    }
    textarea.addEventListener('input', onTextChanged);
    curdata = initData();
    importText(curdata, textarea.value);
    updateHTML(curdata);
}
