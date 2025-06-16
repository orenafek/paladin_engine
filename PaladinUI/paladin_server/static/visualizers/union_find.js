class UnionFind extends Visualizer {

    matches(data) {
        return data != null && typeof data === 'object' && 'parent' in data && Array.isArray(data['parent']) &&
            'rank' in data && Array.isArray(data['rank']);
    }

    format(data) {
        return {
            type: "htmlElement",
            content: this.renderUF(data)
        }
    }

    renderUF(data) {
        const width = 300;
        const height = 200;

        // Define color scale for different groups
        const color = d3.scaleOrdinal(d3.schemeDark2);

        const parent = data['parent'];
        const rank = data['rank']

        let nodes = parent.map((_, i) => ({id: i}));
        const links = parent.map((p, i) => ({source: i, target: p, value: rank[i]}));

        // Create a simulation with several forces.
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id))
            .force("charge", d3.forceManyBody())
            .force("x", d3.forceX())
            .force("y", d3.forceY())
            .on("tick", ticked);

        // Create the SVG container.
        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [-width / 2, -height / 2, width, height])
            .attr("style", "max-width: 100%; height: auto;");

        // Add a line for each link, and a circle for each node.
        const link = svg.append("g")
            .attr("class", 'uf-edge')
            .selectAll("line")
            .data(links)
            .join("line");

        const node = svg.append("g")
            .attr("class", "uf-node")
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", 10)
            .attr("fill", d => color(parent[d.id]));


        const nodeText = svg.append("g")
            .selectAll("text")
            .data(nodes)
            .enter().append("text")
            .text(d => d.id)
            .attr("class", "uf-node-text");

        // Add a drag behavior.
        node.call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

        function ticked() {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            nodeText
                .attr("x", d => d.x)
                .attr("y", d => d.y);


        }

        // Reheat the simulation when drag starts, and fix the subject position.
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        // Update the subject (dragged node) position during drag.
        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        // Restore the target alpha so the simulation cools after dragging ends.
        // Unfix the subject position now that it’s no longer being dragged.
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        //language=css
        Visualizer.addStyle(`
            svg {
                width: ${width}px;
                height: ${height}px;
            }

            .uf-node {
            }

            .uf-edge {
                stroke: none;
                fill: none;
            }

            .uf-node-text {
                font-size: 10pt;
                text-anchor: middle;
                dominant-baseline: central;
                fill: white; /* Change text color to red */
            }

            .uf-rank {
                font-size: 10px;
                text-anchor: middle;
                dominant-baseline: middle;
                fill: hotpink; /* Change rank text color to blue */
            }
        `);

        return svg.node();
    }
}