import {createApp} from "vue";

//@ts-ignore
import Main from "./components/main.vue";
import {createVuestic} from "vuestic-ui";

function main() {
    let app = createApp(Main)
        .use(createVuestic())
        .mount(document.querySelector('#app'));

    Object.assign(window, {app});
}

document.addEventListener('DOMContentLoaded', main);