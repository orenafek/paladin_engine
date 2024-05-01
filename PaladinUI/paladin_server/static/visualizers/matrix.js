class MatrixVisualizer {

    matches(data) {
        return Array.isArray(data) && data.length > 0 && data.every(row => Array.isArray(row));
    }

    format(data) {
        return {
            type: "htmlElement",
            content: this.renderMatrix(data)
        }
    }

    renderMatrix(data) {
        const numRows = data.length;
        const numCols = data[0].length;
        const cellSize = 20; // Smaller cell size
        const padding = 2; // Reduced padding

        // Calculate total width and height of the matrix
        const width = numCols * cellSize + (numCols + 1) * padding;
        const height = numRows * cellSize + (numRows + 1) * padding;

        // Create SVG container
        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", `0 0 ${width} ${height}`)
            .attr("style", "max-width: 100%; height: auto;");

        // Render cells
        for (let i = 0; i < numRows; i++) {
            for (let j = 0; j < numCols; j++) {
                // Calculate position for each cell
                const x = j * (cellSize + padding) + padding;
                const y = i * (cellSize + padding) + padding;

                // Create cell rectangle
                svg.append("rect")
                    .attr("x", x)
                    .attr("y", y)
                    .attr("width", cellSize)
                    .attr("height", cellSize)
                    .attr("fill", "none") // No background
                    .attr("stroke", "white") // White border
                    .attr("stroke-width", 1); // Border width

                // Add text inside the cell with white foreground color
                svg.append("text")
                    .attr("x", x + cellSize / 2)
                    .attr("y", y + cellSize / 2)
                    .attr("dy", "0.35em")
                    .attr("text-anchor", "middle")
                    .attr("fill", "white") // White foreground color
                    .text(data[i][j]);
            }
        }

        return svg.node();
    }


}
