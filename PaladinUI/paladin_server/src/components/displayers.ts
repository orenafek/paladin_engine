import {ref, Ref} from "vue";

type FormattedData = {
    type: string
    content: string
}

interface DisplayClass {
    matches(data: any): string
    format(data: any): FormattedData
}

type Displayer = {
    name: string
    icon: string
    active: boolean
    file: string
    source?: string
    instance?: DisplayClass
}

class Displayers {
    readonly DISPLAYERS_FOLDER: string = '../../static/customizers/';

    static instance = new Displayers()

    displayers: Ref<Displayer[]> = ref([])
    active: Ref<Displayer[]> = ref([])

    async loadDisplayers(displayers: Displayer[]) {
        this.displayers.value = await Promise.all(displayers.map(async (d: Displayer) => {
            d.source = await (await fetch(this.DISPLAYERS_FOLDER + d.file)).text();
            d.instance = this.instantiate(d.source);
            return d;
        }));
    }

    private instantiate(source: string): DisplayClass {
        let clazz = eval(`(${source})`);
        return new clazz();
    }

    activate(name: string) {
        const index = this.indexOf(name);
        if (index >= 0) {
            this.active.value.push(this.displayers.value[index]);
        }
    }

    deactivate(name: string) {
        const index = this.indexOf(name);
        if (index >= 0){
            const displayer = this.displayers.value[index];
            const activeIndex = this.active.value.indexOf(displayer);

            if (activeIndex >= 0){
                this.active.value = [];
            }
        }
    }

    deactivateAll() {
        this.active.value.splice(0, this.active.value.length);
    }
    private indexOf(name: string) : number{
        for (let i = 0; i < this.displayers.value.length; i++) {
            if (this.displayers.value[i].name === name){
                return i;
            }
        }
        return -1;
    }

}

export {FormattedData, DisplayClass, Displayer, Displayers};
