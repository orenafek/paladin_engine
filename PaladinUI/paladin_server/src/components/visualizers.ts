import {ref, Ref} from "vue";

import {Visualizer as VisualizerBase}  from "../../static/visualizers/visualizer";

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

const VISUALIZERS_FOLDER: string = '../../static/visualizers/';
const VISUALIZER_BASE_CLASS_PATH: string = VISUALIZERS_FOLDER + "visualizer.js";

class Visualizers {

    static instance: Visualizers = new Visualizers()

    builtin: Ref<Visualizer[]> = ref([])

    async loadBuiltinVisualizers(visualizers: Visualizer[]) {
        window['Visualizer'] = VisualizerBase;
        this.builtin.value = await Promise.all(visualizers.map(async (d: Visualizer) => {
            d.source = await (await fetch(VISUALIZERS_FOLDER + d.file)).text();
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
