// noinspection DuplicatedCode

class Customizer {

    matches(data) {
        function isEdge(obj) {
            return typeof obj === 'object' &&
                'dest' in obj && typeof obj.dest !== 'undefined' &&
                'src' in obj && typeof obj.src !== 'undefined' &&
                'weight' in obj && typeof obj.weight !== 'undefined'
        }

        return (Array.isArray(data) && data.every(obj => isEdge(obj))) || data && isEdge(data);

    }

    format(data) {
        return {
            type: "htmlElement",
            content: this.renderD3Graph(data)
        }
    }

    renderD3Graph(data) {
        // Specify the dimensions of the chart.
        const width = 300;
        const height = 200;

        // Specify the color scale.
        const color = d3.scaleOrdinal(d3.schemeCategory10);

        data = Array.isArray(data) ? data : [data];

        const nodes = [...new Set(data.flatMap(edge => [edge.src, edge.dest]))].map(id => ({id}));

        const links = data.map(edge => ({
            source: edge.src,
            target: edge.dest,
            value: edge.weight
        }));

        // Create a simulation with several forces.
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2))
            .on("tick", ticked);

        // Create the SVG container.
        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .attr("style", "max-width: 100%; height: auto;");

        // Add a <g> element for each link and node.
        const linkGroup = svg.append("g").attr("class", "graph-edge");
        const nodeGroup = svg.append("g").attr("class", "nodes");

        // Add a line for each link, and a circle for each node.
        const link = linkGroup
            .selectAll("line")
            .data(links)
            .join("line")
            .attr('stroke-width', d => Math.sqrt(d.value));

        const linkText = linkGroup.selectAll("text")
            .data(links)
            .join('text')
            .text(d => d.value)
            .attr('class', 'graph-edge-text')
            .attr("x", d => (d.source.x + d.target.x) / 2) // Position text in the middle of the line
            .attr("y", d => (d.source.y + d.target.y) / 2) // Position text in the middle of the line
            .attr("dy", "-0.5em") // Adjust vertical position
            .attr("text-anchor", "middle"); // Center text horizontally

        const node = nodeGroup.selectAll("g")
            .data(nodes)
            .enter().append("g");

        node.append("circle")
            .attr("r", 10)
            .attr("class", "graph-node");

        // Add title inside the circle for each node.
        node.append("text")
            .text(d => d.id)
            .attr("class", "graph-node-text")
            .attr("text-anchor", "middle");

        // Add a drag behavior.
        node.call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

        // Set the position attributes of links and nodes each time the simulation ticks.
        function ticked() {
            link.attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            // linkText
            //     .attr('x', d => 0.5 * (d.source.x + d.target.x))
            //     .attr('y', d => 0.5 * (d.source.y + d.target.y));

            linkText
                .attr('x', d => calcTextPos(d, 'x'))
                .attr('y', d => calcTextPos(d, 'y'));

            node.attr("transform", d => `translate(${d.x},${d.y})`);
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
        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        function calcTextPos(d, coord) {
            // Calculate the mid-point of the line
            const midX = (d.source.x + d.target.x) / 2;
            const midY = (d.source.y + d.target.y) / 2;

            // Calculate the angle of the line
            const angle = Math.atan2(d.target.y - d.source.y, d.target.x - d.source.x);

            // Adjust the text position based on the angle
            if (coord === 'x') {
                return midX + Math.cos(angle) * 10; // Adjust 10 for distance from line
            } else {
                return midY + Math.sin(angle) * 10; // Adjust 10 for distance from line
            }
        }

        /* language=css */
        const cssStyles = `
            .graph-node {
                fill: #eb6734;
                stroke: #eb6734;
            }

            .graph-edge {
                stroke: #ffc66d;
            }

            .graph-node-text {
                font-size: 12px;
                text-anchor: middle;
                dominant-baseline: central;
                fill: white; /* Change text color to red */
            }

            .graph-edge-text {
                font-size: 10pt;
                stroke: white;
            }

            .graph-rank {
                font-size: 10px;
                text-anchor: middle;
                dominant-baseline: middle;
                fill: hotpink; /* Change rank text color to blue */
            }
        `

        const styleTag = document.createElement('style');
        styleTag.textContent = cssStyles;
        document.head.appendChild(styleTag);

        return svg.node();
    }

}