import {ref, Ref} from "vue";

type FormattedData = {
    type: string
    content: string
}

interface DisplayClass {
    matches(data: any): string

    format(data: any): FormattedData
}

type Visualizer = {
    name: string
    icon: string
    file: string
    source?: string
    instance?: DisplayClass
}

class Visualizers {
    readonly VISUALIZERS_FOLDER: string = '../../static/visualizers/';

    static instance: Visualizers = new Visualizers()

    builtin: Ref<Visualizer[]> = ref([])

    async loadBuiltinVisualizers(visualizers: Visualizer[]) {
        this.builtin.value = await Promise.all(visualizers.map(async (d: Visualizer) => {
            d.source = await (await fetch(this.VISUALIZERS_FOLDER + d.file)).text();
            d.instance = this.instantiate(d.source);
            return d;
        }));
    }

    private instantiate(source: string): DisplayClass {
        let clazz = eval(`(${source})`);
        return new clazz();
    }

    matches(data: string): Visualizer[] {
        return this.builtin.value.filter(v => v.instance.matches(data));
    }
}

export {FormattedData, DisplayClass, Visualizer, Visualizers};
