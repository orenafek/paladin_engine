import {createApp} from "vue";

//@ts-ignore
import Main from "./components/main.vue";

function main() {
    let app = createApp(Main).mount(document.querySelector('#app'));

    Object.assign(window, {app});
}

document.addEventListener('DOMContentLoaded', main);