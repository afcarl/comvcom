// helper.ts

const FIELDNAME = 'CommentTaggerData';
const TARGETS = [
    'L:Left', 'R:Right', 'U:Up', 'X:In-place', 'Z:Other'
];
const CATEGORIES = [
    'm:Meta Info.', 'o:Value Desc.',
    'a:Precondition', 'p:Postcondition',
    't:Type/Enum/Iface', 'i:Instruction', 'g:Guide',
    'c:Comment Out', 'v:Visual Cue',
    'd:Directive', 'u:Uncategorized'
];

var textarea: HTMLTextAreaElement = null;

class Item {

    beginning: boolean = false;
    target: string = '';
    category: string = '';
    ungrammatical: boolean = false;
    updated: number = 0;

    load(cols: string[]) {
        this.beginning = (cols[0] == 'true');
        this.target = cols[1];
        this.category = cols[2];
        this.ungrammatical = (cols[3] == 'true');
        this.updated = parseInt(cols[4]);
    }

    save() {
        return (this.beginning+','+this.target+','+
                this.category+','+this.ungrammatical+','+
                this.updated);
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
        let cb1 = document.getElementById('CB'+cid) as HTMLInputElement;
        if (cb1 !== null) {
            cb1.checked = item.beginning;
        }
        let sel1 = document.getElementById('ST'+cid) as HTMLSelectElement;
        if (sel1 !== null) {
            sel1.value = item.target;
        }
        let sel2 = document.getElementById('SC'+cid) as HTMLSelectElement;
        if (sel2 !== null) {
            sel2.value = item.category;
        }
        let cb2 = document.getElementById('CG'+cid) as HTMLInputElement;
        if (cb2 !== null) {
            cb2.checked = item.ungrammatical;
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

    function onBChanged(ev: Event) {
        let e = ev.target as HTMLInputElement;
        let cid = e.id.substr(2);
        let item = data[cid];
        item.beginning = e.checked;
        item.updated = Date.now();
        textarea.value = exportText(data);
	saveText();
    }

    function onTargetChanged(ev: Event) {
        let e = ev.target as HTMLSelectElement;
        let cid = e.id.substr(2);
        let item = data[cid];
        item.target = e.value;
        item.updated = Date.now();
        textarea.value = exportText(data);
	saveText();
    }

    function onCategoryChanged(ev: Event) {
        let e = ev.target as HTMLSelectElement;
        let cid = e.id.substr(2);
        let item = data[cid];
        item.category = e.value;
        item.updated = Date.now();
        textarea.value = exportText(data);
	saveText();
    }

    function onUngChanged(ev: Event) {
        let e = ev.target as HTMLInputElement;
        let cid = e.id.substr(2);
        let item = data[cid];
        item.ungrammatical = e.checked;
        item.updated = Date.now();
        textarea.value = exportText(data);
	saveText();
    }

    function makeSelect(e: Element, id: string, choices: string[]) {
        let select = document.createElement('select');
        select.id = id;
        for (let k of choices) {
            let i = k.indexOf(':');
            let option = document.createElement('option');
            let v = k.substr(0, i);
            option.setAttribute('value', v);
            option.innerText = v+')'+k.substr(i+1);
            select.appendChild(option);
        }
        e.appendChild(select);
        return select;
    }

    function makeCheckbox(e: Element, id: string, caption: string) {
        let label = document.createElement('label');
        let checkbox = document.createElement('input');
        checkbox.id = id;
        checkbox.setAttribute('type', 'checkbox');
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(' '+caption));
        e.appendChild(label);
        return checkbox;
    }

    for (let e of toArray(document.getElementsByClassName('ui'))) {
        let cid = e.id;
        let cb1 = makeCheckbox(e, 'CB'+cid, 'B?');
        cb1.addEventListener('change', onBChanged);
        e.appendChild(document.createTextNode(' '));
        let sel1 = makeSelect(e, 'ST'+cid, TARGETS);
        sel1.addEventListener('change', onTargetChanged);
        e.appendChild(document.createTextNode(' '));
        let sel2 = makeSelect(e, 'SC'+cid, CATEGORIES);
        sel2.addEventListener('change', onCategoryChanged);
        e.appendChild(document.createTextNode(' '));
        let cb2 = makeCheckbox(e, 'CG'+cid, 'Ung?');
        cb2.addEventListener('change', onUngChanged);
        e.appendChild(document.createTextNode(' '));
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
