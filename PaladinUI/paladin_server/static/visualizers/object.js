class ObjectTree extends Visualizer {

    matches(data) {
        return typeof data === 'object' && data !== null;
    }

    format(data) {
        return {
            type: "htmlElement",
            content: this.renderObject(data)
        }
    }

    isList(obj) {
        return Array.isArray(obj) || Object.keys(obj).every(key => Number.isInteger(parseInt(key)));
    }


    renderObject(d) {
        const table = document.createElement('table');
        table.classList.add('object-table'); // Add CSS class 'object-table'
        const tbody = document.createElement('tbody');

        if (this.isList(d)) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');

            const span = document.createElement('span');
            d.forEach((value, index) => {
                if (typeof value === 'object' && value !== null) {
                    if (index > 0) {
                        span.appendChild(document.createTextNode(', ')); // Add comma as delimiter
                    }
                    span.appendChild(this.renderObject(value)); // Render object recursively
                } else {
                    if (index > 0) {
                        span.appendChild(document.createTextNode(', ')); // Add comma as delimiter
                    }
                    const spanValue = document.createElement('span');
                    spanValue.textContent = value;
                    span.appendChild(spanValue);
                }
            });
            td.appendChild(span);
            tr.appendChild(td);
            tbody.appendChild(tr);
        } else {
            for (let key in d) {
                const tr = document.createElement('tr');
                const tdKey = document.createElement('td');
                const tdValue = document.createElement('td');

                if (typeof d[key] === 'object' && d[key] !== null) {
                    tdKey.textContent = key;
                    tdValue.setAttribute('colspan', '2');
                    tdValue.appendChild(this.renderObject(d[key]));
                    tr.appendChild(tdKey);
                    tr.appendChild(tdValue);
                } else {
                    tdKey.textContent = key;
                    tdValue.textContent = d[key];
                    tr.appendChild(tdKey);
                    tr.appendChild(tdValue);
                }

                tbody.appendChild(tr);
            }
        }

        // language=CSS
        Visualizer.addStyle(`
        .object-table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
            border: 2px solid #ff8c00; /* Vivid orange border */
        }

        .object-table ™th, .object-table td {
            padding: 8px;
            border: none; /* No borders between cells */
            color: white; /* White text color */
        }

        .object-table th {
            background-color: #f29400; /* Darker orange for header */
        }

        .object-table .object-key {
            font-weight: bold;
        }

        .object-table .object-value {
            font-weight: normal;
        }

        .object-table tr:first-child th {
            /*border-top: 1px solid #fff; !* White border for top of first row *!*/
        }

        .object-table tr:last-child td {
            /*border-bottom: 1px solid #fff; !* White border for bottom of last row *!*/
        }`);

        table.appendChild(tbody);
        return table;
    }
}