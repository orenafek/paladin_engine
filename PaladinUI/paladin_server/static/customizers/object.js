class Customizer {

    matches(data) {
        return data?.hasOwnProperty('start');

    }

    format(data) {
        return {
            type: "text/html",
            content:
                `<table>
                    <tr style="color:yellow">
                        <td v-for="element in data.arr">{{element}}</td>
                    </tr>
                    <tr style="color:red">
                        <td v-for="(element, index) in data.arr">
                            <span v-if="index === data.start">i</span>
                            <span v-else-if="index === data.end">j</span>
                        </td>
                    </tr>
                </table>`

        }
    }
}