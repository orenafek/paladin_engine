class Customizer {

    matches(data) {
        return data !== null;

    }

    format() {
        return {
            type: "text/html",
            content:
                `
                <table style="border-collapse: collapse;">
                    <tr style="color: yellow">
                        <template v-for="(item, index) in data.arr">
                            <td v-if="(index >= (data.low ?? undefined)) && index <= (data.high ?? undefined)" style="border: 1px solid white; background-color: lightpink;">
                                {{item}}
                            </td>
                            <td v-else style="border: 1px solid white; border-collapse: collapse;">
                                {{item}}
                            </td>
                        </template>
                    </tr>
                    <tr style="color: red">
                        <td v-for="(_, index) in data.arr">
                            <span v-if="[data.high, (data.i > 0 ? data.i : undefined), data.j].includes(index)">
                                <span>&#8593;</span>
                            </span>
                        </td>
                    </tr>
                    <tr>
                        <td v-for="(_, index) in data.arr">
                            <span v-if="index === (data.high ?? undefined)">
                                p
                            </span>
                            <span v-if="index === (data.i ?? undefined) && data.i > 0">
                                i
                            </span>
                            <span v-if="index === (data.j ?? undefined)">
                                j
                            </span>
                        </td>
                    </tr>
                </table>
                `

        }
    }
}